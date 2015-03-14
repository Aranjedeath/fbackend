import datetime

from app import db
from sqlalchemy.sql import text


def average_upvote_count(user_id):
    results = db.session.execute(text("""SELECT COUNT(1) as upvote_count
                                                FROM question_upvotes JOIN questions ON questions.id=question_upvotes.question
                                                WHERE questions.question_author=:user_id
                                                    AND questions.deleted=false
                                                    AND question_upvotes.downvoted=false
                                                    AND question_upvotes.timestamp>=:last_two_months
                                        """),
                                    params={'user_id':user_id,
                                            'last_two_months':datetime.datetime.now() - datetime.timedelta(days=60)
                                            }
                                )
    upvote_count = 0
    for row in results:
        upvote_count = row[0]

    results = db.session.execute(text("""SELECT COUNT(1)
                                            FROM questions
                                            WHERE questions.question_author=:user_id
                                                AND questions.deleted=false
                                                AND questions.timestamp>=:last_two_months
                                        """),
                                    params={'user_id':user_id,
                                            'last_two_months':datetime.datetime.now() - datetime.timedelta(days=60)
                                            }
                                )
    question_count = 0
    for row in results:
        question_count = row[0]
    upvote_count += question_count

    average_upvote_count = upvote_count/question_count
    return average_upvote_count

def list_objects_with_notifications_pushed(user_id, notification_type, day_count=1):
    object_id = []
    result = db.session.execute(text("""SELECT notifications.object_id
                                        FROM user_push_notifications JOIN notifications 
                                            ON user_push_notifications.notification_id=notifications.id
                                        WHERE user_push_notifications.user_id=:user_id
                                            AND notifications.type=:notification_type
                                            AND user_push_notifications.pushed_at>:time_period
                                    """),
                                params={
                                        'user_id':user_id,
                                        'notification_type':notification_type,
                                        'time_period':datetime.datetime.now()-datetime.timedelta(days=day_count)
                                        }
                                )
    for row in result:
        notification_count = row[0]
    return notification_count


def decide_question_ask_notification(question_id, user_id):
    if average_upvote_count(user_id)<3 and count_of_notifications_pushed(user_id, 'question-ask-self_user')<1:
        return True
    else:
        return False

def get_most_upvoted_questions(user_id):
    questions_with_count = []
    after_date = datetime.datetime.now()
    before_date = after_date - datetime.timedelta(days=1)
    results = db.session.execute(text("""SELECT question_upvotes.question, COUNT(1) as upvote_count
                                                FROM question_upvotes JOIN questions ON questions.id=question_upvotes.question
                                                WHERE questions.queston_author=:user_id
                                                    AND question_upvotes.downvoted=false
                                                    AND question_upvotes.timestamp>=:after_date
                                                    AND question_upvotes.timestamp<:before_date
                                                ORDER BY upvote_count
                                                LIMIT 0, 10
                                        """),
                                    params={
                                            'user_id':user_id,
                                            'after_date':after_date,
                                            'before_date':before_date
                                            }
                                )
    for row in results:
        questions_with_count.append({'question_id':row[0], 'upvote_count':row[1]})

def question_for_todays_upvoted_notification(user_id):








