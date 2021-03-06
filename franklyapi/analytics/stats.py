import datetime
import json

from sqlalchemy.sql import text, func
from app import db
from models import *
from mail import admin_email
from models import User
from stats_html_helper import *
from configs import production_config as config
from stats_queries import *


def weekly_macro_metrics():

    questions_asked = day_distribution_questions_asked()
    questions_answered = day_distribution_questions_answered()
    video_views = day_distribution_video_views()

    report = "Frankly weekly report dating back 7 days from %s " % str(datetime.datetime.now().date())
    report += "<table border='1'><tbody><tr>" \
                "<th>Day</th>" \
                "<th>Questions Asked</th>" \
                "<th>Questions Answered</th>" \
                "<th>Video Views</th></tr>"
    for i in range(7):
        day = (datetime.datetime.now() - datetime.timedelta(days=i + 1))
        report += day.strftime('<tr><td> %A %d  %B </td>')
        report += "<td> %s </td>" % str(questions_asked[i])
        report += "<td> %s </td>" % str(questions_answered[i])
        report += "<td> %s </td>" % str(video_views[i])
        report += "</tr>"

    report += "</tbody></table>"
    admin_email.send_weekly_report(config.WEEKLY_MAIL_RECIPIENTS, report)


def daily_content_report():



    msg1 = make_panel('Usernames of people asking 3 or more questions',
                       users_asking_questions_more_than_or_equal_to(3))

    msg2 = make_panel('Usernames of people who have been asked 3 or more questions',
                       users_being_asked_questions_more_than_or_equal_to(3))

    msg3 = make_panel('Links of top 20 questions with the most (real) upvotes',
                      questions_with_most_upvotes(20))

    msg4 = make_panel('Usernames of top 20 people with the highest increase'
                      ' in follows (real follows)',
                      users_with_highest_increase_in_follows(20))

    msg5 = make_panel('Links of top 20 questions with the highest likes (real)', questions_with_highest_likes(20))

    msg6 = make_panel('Links of top 20 questions with the highest comments (real)', questions_with_highest_comments(20))

    msg7 = make_panel("Question askers for Jatin Sapru: ", question_askers_for_sapru())

    body = add_style() + msg1 + msg2 + msg3 + msg4 + msg5 + msg6 + msg7

    admin_email.content_report(config.DAILY_CONTENT_MAIL_RECIPIENTS, 'Daily Report', body)


def intra_day_content_report(interval):

    msg1 = make_panel('New registrations (celeb and non-celeb) in last 12 hours  Source '
                      '& number of registrations', new_registrations(interval))

    msg2 = make_panel('No. of questions asked (excluding those from the dashboard)', count_of_question_asked(interval))

    msg3 = make_panel('Videos uploaded   (celeb and non-celeb) with link', videos_uploaded(interval))

    body = add_style() + msg1 + msg2 + msg3

    admin_email.content_report(config.DAILY_CONTENT_MAIL_RECIPIENTS, 'Twice a day Report', body)


def day_distribution_questions_asked():
    result = []
    for i in range(1, 8):
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).date()
        result.append(number_of_questions_asked([0], 1, day))
    return result


def day_distribution_questions_answered():
    result = []
    for i in range(1, 8):
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).date()
        result.append(number_of_answers_uploaded([0], 1, day))
    return result


def day_distribution_video_views():
    result = []
    for i in range(1, 14):
        day = (datetime.datetime.now() - datetime.timedelta(days=i)).date()
        result.append(number_of_videos_viewed(1, day))
    return result


def number_of_videos_viewed(day_count, end_date=datetime.datetime.now(), range_type="single_day"):

    start_of_time_period, end_of_time_period = time_delta(day_count, end_date, range_type)

    last_view_count = db.session.query(func.max(Stats.total_video_view_count)). \
                       filter(Stats.counted_on <= start_of_time_period).one()[0]

    current_view_count = int(db.session.query(func.sum(Post.view_count)).one()[0])

    if last_view_count is not None:
        return current_view_count - last_view_count
    else:
        return None


def number_of_answers_uploaded(user_types, day_count, end_date=datetime.datetime.now(), range_type="single_day"):
    start_of_time_period, end_of_time_period = time_delta(day_count, end_date, range_type)
    answer_query = Post.query.join(User, User.id == Post.answer_author
                            ).filter(User.user_type.in_(user_types),
                                     Post.deleted == False,
                                     Post.timestamp < end_of_time_period,
                                     Post.timestamp >= start_of_time_period
                            )
    total_answer_count = answer_query.count()

    #answer_list = answer_query.order_by(Post.timestamp).limit(50)

    return total_answer_count # {'total_count':total_answer_count, 'answer_list':answer_list}

def number_of_questions_asked(user_types, day_count, end_date=datetime.datetime.now(), range_type="single_day"):
    start_of_time_period, end_of_time_period = time_delta(day_count, end_date, range_type)
    question_query = Question.query.join(User, Question.question_to == User.id
                                    ).filter(
                                                User.user_type.in_(user_types),
                                                Question.added_by == None,
                                                Question.timestamp < end_of_time_period,
                                                Question.timestamp >= start_of_time_period
                                    )
    question_count = question_query.count()

    return question_count


# To be run daily
def video_view_count_logger():
    total_view_count = Post.query.with_entities(func.sum(Post.view_count).label('sum'))[0][0]
    date = datetime.datetime.now()
    db.session.execute(text("Insert into stats (total_video_view_count,counted_on) values (:view_count,:date)"),
                       params={'view_count':total_view_count, 'date':date})
    db.session.commit()


def number_of_users_registered(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    user_query = User.query.filter(
                                    User.user_type.in_(user_types),
                                    User.user_since < end_of_time_period,
                                    User.user_since >= start_of_time_period
                                 )

    total_user_count = user_query.count()

    user_list = user_query.order_by(User.user_since).limit(50).all()

    return {'total_count':total_user_count, 'user_list':user_list}


def registration_type_wise_user_count(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    results = db.session.execute(text("""SELECT users.registered_with, COUNT(1) as user_count FROM users
                                            WHERE users.user_type in :user_types
                                                AND users.user_since < :end_of_time_period
                                                AND users.user_since >= :start_of_time_period
                                            GROUP BY users.registered_with
                                        """),
                                    params={'user_types':user_types,
                                            'end_of_time_period':end_of_time_period,
                                            'start_of_time_period':start_of_time_period
                                            }
                                    )
    data = {row[0]:row[1] for row in results}
    return data


def users_who_added_profile_videos(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    user_query = User.query.filter(  
                                    User.profile_video != None,
                                    User.user_since < end_of_time_period,
                                    User.user_since >= start_of_time_period
                                )

    total_count = user_query.count()

    user_list = user_query.order_by(User.user_since).limit(50)

    return {'total_count':total_count, 'user_list':user_list}

def time_delta(day_count, end_date, range_type):
    today_timetuple = end_date.timetuple()
    hour, minute = 23, 59
    if range_type != 'single_day':
        hour, minute = 0, 0

    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=hour, minute=minute, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    return start_of_time_period, end_of_time_period



def send_daily_mail_old(day_count=1, emails=['shashank@frankly.me']):
    registered_celebs_today = number_of_users_registered(user_types=[2], day_count=day_count)
    celeb_register_count = registered_celebs_today['total_count']
    celebs = registered_celebs_today['user_list']
    
    celeb_list = '<br>'.join(['<a href="http://frankly.me/{username}">{first_name}</a>({user_title}), '.format(username=celeb.username,
                                                    first_name=celeb.first_name,
                                                    user_title=celeb.user_title) for celeb in celebs])

    celeb_answers_today = number_of_answers_uploaded(user_types=[2], day_count=day_count)

    celeb_answer_count = celeb_answers_today['total_count']
    celeb_answer_list = celeb_answers_today['answer_list']

    answer_list_text = []

    for answer in celeb_answer_list:
        question = Question.query.filter(Question.id == answer.question).one()
        answer_author = User.query.filter(User.id == answer.answer_author).one()
    
        answer_list_text.append('<a href="http://frankly.me/{username}">{first_name}</a>({user_title}) : <a href="http://frankly.me/p/{short_id}">{question_text}{contd}</a>, '.format(username=answer_author.username,
                                                                                    first_name=answer_author.first_name,
                                                                                    user_title=answer_author.user_title,
                                                                                    short_id=answer.client_id,
                                                                                    question_text=question.body[:80],
                                                                                    contd='' if question.body<=80 else '...'))
    celeb_answer_list = '<br>'.join(answer_list_text)

    user_answer_count = number_of_answers_uploaded(user_types=[0], day_count=day_count)['total_count']

    total_answer_count = user_answer_count+celeb_answer_count

    registration_counts = registration_type_wise_user_count(user_types=[0], day_count=day_count)
    total_registration_count = sum(registration_counts.values())
    registration_counts = json.dumps(registration_counts, indent=4).replace('\n', '<br>')

    questions_asked_to_celebs = number_of_questions_asked([2], day_count=day_count)['question_count']
    questions_asked_to_other_users = number_of_questions_asked([0], day_count=day_count)['question_count']
    total_question_count = questions_asked_to_celebs+questions_asked_to_other_users

    email_text = """
<br><b>User Registrations_today</b>: {total_registration_count}
<br>{registration_counts}
<br><br>
----------------------------------------------
<br><b>Questions Asked</b>: {total_question_count}
<br>Questions to Celebs = {questions_asked_to_celebs}
<br>Questions to Users = {questions_asked_to_other_users}
<br><br>
----------------------------------------------
<br><b>Answers Uploaded</b>: {total_answer_count}
<br>Answers by Celebs = {celeb_answer_count}
<br>Answers by Users = {user_answer_count}
<br><br>
----------------------------------------------
<br><b>Celebs registered</b>: {celeb_register_count}
<br>{celeb_list}
<br><br>
----------------------------------------------
<br><b>Celeb Answers Uploaded Today</b>: {celeb_answer_count}
<br>{celeb_answer_list}
<br><br>

    """.format(total_registration_count=total_registration_count,
               registration_counts=registration_counts,
               total_question_count=total_question_count,
               questions_asked_to_celebs=questions_asked_to_celebs,
               questions_asked_to_other_users=questions_asked_to_other_users,
               total_answer_count=total_answer_count,
               user_answer_count=user_answer_count,
               celeb_register_count=celeb_register_count,
               celeb_list=celeb_list,
               celeb_answer_count=celeb_answer_count,
               celeb_answer_list=celeb_answer_list)

    from controllers import mailer
    message_subject = 'Stats for {date}'.format(date=datetime.datetime.strftime(datetime.datetime.now(), '%d-%b-%Y, %a'))
    for email in emails:
        mailer.send_mail(reciever_id=email, message_subject=message_subject, message_body=email_text)

