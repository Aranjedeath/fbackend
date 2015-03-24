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
    from models import *
    from app import db
    import async_encoder
    import datetime
    count = 1
    videos = Video.query.filter(Video.process_state.in_(['pending', 'failed'])).all()
    for v in videos:
        post = Post.query.with_entities('id', 'answer_author').filter(Post.media_url==v.url).first()
        if post:
            v.video_type='answer_video'
            v.object_id=post.id
            v.username=User.query.with_entities('username').filter(User.id==post.answer_author).one().username
        else:
            user = User.query.with_entities('id', 'username').filter(User.profile_video==v.url).first()
            if user:
                v.username=user.username
                v.video_type='profile_video'
                v.object_id=user.id
            else:
                v.delete = True
        db.session.add(v)
        db.session.commit()
        if not v.delete and (datetime.datetime.now() - v.created_at).seconds > 1800:
            async_encoder.encode_video_task.delay(v.url, username=v.username, redo=True)
        print count
        count += 1

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
    except Exception as e:
         email_helper.cron_job_update(args[0], traceback.format_exc(e))



