from video_db import update_view_count_to_db, redis_views, update_total_view_count
from app import db
from models import User
from analytics import stats
from mail import admin_email
from notification import notification_decision, push_notification

import datetime
import async_encoder
import traceback

'''
@ 00:00 every day
'''
def log_video_count():
    stats.video_view_count_logger()

'''
@ 00:30 every day
'''
def decide_popular_users_based_on_questions_asked():
    notification_decision.decide_popular_users()

'''
@ 10 AM Every day
'''
def push_stats():
    push_notification.stats()

'''
@ Every 5 minutes
'''
def update_view_count():
    print 'started'
    for url in redis_views.keys():
        update_view_count_to_db(url)
    print 'ended'

'''
@ Every 10 minutes
'''
def update_user_view_count():
    users = User.query.with_entities(User.id).filter(User.user_type==2)
    update_total_view_count([user.id for user in users])


'''
@ Every hour
'''
def reassign_pending_video_tasks():
    import datetime
    from sqlalchemy import text
    # videos = Video.query.filter(Video.process_state.in_(['pending', 'failed'])).all()
    retry_queue='encoding_retry'
    low_priority_queue='encoding_low_priority'
    virgin_videos = db.session.execute(text(
                                            """SELECT v.url, v.object_id, v.video_type, v.username,
                                                v.created_at, u.user_type, v.opt, v.medium, v.low, v.ultralow, v.promo
                                                FROM videos v LEFT JOIN users u ON v.username = u.username 
                                                WHERE v.opt IS NULL
                                                    AND v.low IS NULL
                                                    AND v.medium IS NULL
                                                    AND v.promo IS NULL
                                                    AND v.ultralow IS NULL
                                                    AND v.delete = 0
                                                    AND v.created_at > :begin_time
                                                ORDER BY u.user_type DESC
                                            """
                                            ),
                                        params = dict(begin_time=datetime.datetime.now()-datetime.timedelta(days=2))
                                        )

    assigned_urls = []
    for v in virgin_videos:
        if (datetime.datetime.now() - v.created_at).seconds > 1800:
            async_encoder.encode_video_task.delay(video_url=v.url, username=v.username)
            assigned_urls.append(v.url)
    virgin_video_count = len(assigned_urls)

    other_videos = db.session.execute(text(
                                            """SELECT v.url, v.object_id, v.video_type, v.username,
                                                    v.created_at, u.user_type, v.opt, v.medium, v.low, v.ultralow, v.promo,
                                                    (v.medium IS NOT NULL) OR (v.low IS NOT NULL) OR (v.ultralow IS NOT NULL) AS no_video_made
                                                FROM videos v LEFT JOIN users u ON v.username = u.username
                                                WHERE (v.opt IS NULL
                                                    OR v.low IS NULL
                                                    OR v.medium IS NULL
                                                    OR v.promo IS NULL
                                                    OR v.ultralow IS NULL)
                                                    AND v.delete = 0
                                                    AND v.created_at > :begin_time
                                                    AND v.url NOT IN :assigned_urls 
                                                ORDER BY u.user_type DESC, no_video_made
                                            """
                                            ),
                                        params=dict(assigned_urls=assigned_urls, begin_time=datetime.datetime.now()-datetime.timedelta(days=2))
                                    )

    profiles = ['opt', 'medium', 'low', 'ultralow', 'promo']
    other_video_count = 0
    for v in other_videos:
        if (datetime.datetime.now() - v.created_at).seconds > 1800:
            profiles_to_encode = []
            for profile in profiles:
                if not getattr(v, profile):
                    profiles_to_encode.append(profile)
            #async_encoder.encode_video_task.delay(video_url=v.url, username=v.username, profiles=profiles_to_encode, queues=dict(low=low_priority_queue, ultralow=retry_queue, medium=retry_queue, opt=retry_queue))
            #print profiles_to_encode, v.url
            #other_video_count +=1
    print 'Virgin Videos Assigned:', virgin_video_count
    print 'Other Videos Assigned:', other_video_count




'''
@ 11:00 AM Monday
'''
def weekly_report():
    stats.weekly_macro_metrics()

'''
@ 11:00 AM Every day
'''
def daily_report():
    stats.daily_content_report()

'''
@ 9:00 AM and 6:00 PM Every day
'''
def twice_a_day_report():
    # interval = 15 if 9 am
    # interval = 9  if 6 pm
    stats.intra_day_content_report(interval=15 if datetime.datetime.now().hour > 12 else 9)


'''
@ Every 6 hours
'''
def heartbeat():
    admin_email.cron_job_update()



if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    method_dict = {
    'update_view_count': update_view_count,

    'update_user_view_count': update_user_view_count,

    'reassign_pending_video_tasks':reassign_pending_video_tasks,

    'log_video_count': log_video_count,

    'daily_report': daily_report,

    'daily_report_two': twice_a_day_report,

    'weekly_report': weekly_report,

    'heartbeat': heartbeat,

    'decide_popular': decide_popular_users_based_on_questions_asked,

    'push_stats': push_stats
        }
    try:
        method_dict[args[0]]()
    except Exception as e:
        admin_email.cron_job_update(args[0], traceback.format_exc(e))



