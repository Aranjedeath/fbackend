from datetime import timedelta
from celery.decorators import periodic_task
from video_db import update_view_count_to_db, redis_data_client, update_total_view_count

from configs import config
from celery import Celery

from models import User

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

@periodic_task(run_every=timedelta(seconds=300), queue='periodic')
def update_view_count():
    print 'started'
    for url in redis_data_client.keys():
        update_view_count_to_db(url)
    print 'ended'



@periodic_task(run_every=timedelta(seconds=600), queue='periodic')
def update_user_view_count():
    users = User.query.with_entities(User.id).filter(User.user_type==2)
    update_total_view_count([user.id for user in users])


@periodic_task(run_every=timedelta(seconds=600), queue='periodic')
def update_user_view_count():
    users = User.query.with_entities(User.id).filter(User.user_type==2)
    update_total_view_count([user.id for user in users])