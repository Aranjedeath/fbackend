from celery.decorators import periodic_task
from datetime import timedelta

from video_db import update_view_count_to_db, redis_data_client

@periodic_task(run_every=timedelta(seconds=180), queue='periodic')
def update_view_count():
    for url in redis_data_client.keys():
    	update_view_count_to_db(url)