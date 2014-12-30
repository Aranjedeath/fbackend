from datetime import timedelta
from celery.decorators import periodic_task
from video_db import update_view_count_to_db, redis_data_client

from configs import config
from celery import Celery

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

@periodic_task(run_every=timedelta(seconds=10), queue='periodic')
def update_view_count():
    print 'started'
    for url in redis_data_client.keys():
        print url
        update_view_count_to_db(url)
    print 'ended'