import datetime

from sqlalchemy.sql import text

from app import db
from models import *


def number_of_users_registered(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    user_query = User.query.filter(
                                    User.user_type.in_(user_types),
                                    User.user_since<end_of_time_period,
                                    User.user_since>=start_of_time_period
                                 )

    total_user_count = user_query.count()

    user_list = user_query.order_by(User.user_since).limit(50).all()

    return {'total_count':total_user_count, 'user_list':user_list}

def number_of_answers_uploaded(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    answer_query = Post.query.join(User, User.id==Post.answer_author
                            ).filter(
                                        User.user_type.in_(user_types),
                                        Post.deleted==False,
                                        Post.timestamp<end_of_time_period,
                                        Post.timestamp>=start_of_time_period
                            )
    total_answer_count = answer_query.count()

    answer_list = answer_query.order_by(Post.timestamp).limit(50)

    return {'total_count':total_answer_count, 'answer_list':answer_list}

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
                                    User.profile_video!=None,
                                    User.user_since<end_of_time_period,
                                    User.user_since>=start_of_time_period
                                )

    total_count = user_query.count()

    user_list = user_query.order_by(User.user_since).limit(50)

    return {'total_count':total_count, 'user_list':user_list}

def number_of_questions_asked(user_types, day_count, end_date=datetime.datetime.now()):
    today_timetuple = end_date.timetuple()
    end_of_time_period = datetime.datetime(year=today_timetuple.tm_year, month=today_timetuple.tm_mon,
                                           day=today_timetuple.tm_mday, hour=0, minute=0, second=0)
    start_of_time_period = end_of_time_period - datetime.timedelta(days=day_count)

    question_query = Question.query.join(User, Question.question_to==User.id
                                    ).filter(   
                                                User.user_type.in_(user_types),
                                                Question.added_by==None,
                                                Question.timestamp<end_of_time_period,
                                                Question.timestamp>=start_of_time_period
                                    )
    question_count = question_query.count()
    return {'question_count':question_count}




