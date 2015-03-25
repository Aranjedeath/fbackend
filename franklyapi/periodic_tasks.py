from datetime import timedelta
from celery.decorators import periodic_task
from video_db import update_view_count_to_db, redis_views, update_total_view_count

from configs import config
from celery import Celery
from app import db

from models import User, Video, Post
import async_encoder
 
from analytics import stats
from mailwrapper import email_helper
import traceback


celery = Celery('tasks')
celery.config_from_object('periodic_tasks_config')
 

@celery.task
def update_view_count():
    print 'started'
    for url in redis_views.keys():
        update_view_count_to_db(url)
    print 'ended'



@celery.task
def update_user_view_count():
    users = User.query.with_entities(User.id).filter(User.user_type==2)
    update_total_view_count([user.id for user in users])


@celery.task
def reassign_pending_video_tasks():
    from app import db
    import async_encoder
    import datetime
    from sqlalchemy import text
    count = 1
    # videos = Video.query.filter(Video.process_state.in_(['pending', 'failed'])).all()
    retry_queue='encoding_retry'
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
            ORDER BY u.user_type DESC
        """
        )
    )

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
            ORDER BY u.user_type DESC, no_video_made
        """
        )
    )

    for v in virgin_videos:
        if (datetime.datetime.now() - v.created_at).seconds > 1800:
            async_encoder.encode_video_task.delay(video_url=v.url, username=v.username)
            print v.url

    profiles = ['opt', 'medium', 'low', 'ultralow', 'promo']
    for v in other_videos:
        if (datetime.datetime.now() - v.created_at).seconds > 1800:
            profiles_to_encode = []
            for profile in profiles:
                if not getattr(v, profile):
                    profiles_to_encode.append(profile)

            async_encoder.encode_video_task.delay(video_url=v.url, username=v.username, profiles=profiles_to_encode, queues=dict(low=retry_queue, ultralow=retry_queue, medium=retry_queue, opt=retry_queue))
            print v.url

@celery.task
def log_video_count():
    stats.video_view_count_logger()




@celery.task
def weekly_report():
    stats.weekly_macro_metrics()



@celery.task
def daily_report():
    stats.daily_content_report()



@celery.task
def twice_a_day_report():
    stats.intra_day_content_report()


@celery.task
def heartbeat():
    email_helper.cron_job_update()



if __name__ == '__main__':
    import sys
    args = sys.argv[1:]

    try:
        if args[0] == 'update_view_count':
            update_view_count()
        elif args[0] == 'update_user_view_count':
            update_user_view_count()
        elif args[0] == 'reassign_pending_video_tasks':
            reassign_pending_video_tasks()
        elif args[0] == 'log_video_count':
            log_video_count()
        elif args[0] == 'daily_report':
            daily_report()
        elif args[0] == 'daily_report_two':
            twice_a_day_report()
        elif args[0] == 'weekly_report':
            weekly_report()
        elif args[0] == 'heartbeat':
            heartbeat()
        elif args[0] == 'reassign_pending_video_tasks':
            reassign_pending_video_tasks()
    except Exception as e:
         email_helper.cron_job_update(args[0], traceback.format_exc(e))



