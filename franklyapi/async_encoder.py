import media_uploader
import video_encoder
from configs import config
from celery import Celery
import video_db

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)


@cel.task(queue='encoding')
def encode_video_task(video_url, username='', profiles=video_encoder.VIDEO_ENCODING_PROFILES.keys(), redo=False):
    file_path = media_uploader.download_file(video_url)
    for profile_name in profiles:
    	if redo or not video_db.video_already_encoded(video_url=video_url, video_quality=profile_name):
        	log_id = video_db.add_video_encode_log_start(video_url=video_url, video_quality=profile_name)
        	_encode_video_to_profile(file_path, video_url, profile_name, log_id, username)

@cel.task(queue='encoding')
def _encode_video_to_profile(file_path, video_url, profile,log_id, username=''):
    result = video_encoder.encode_video_to_profile(file_path, video_url, profile, username)
    video_db.update_video_encode_log_finish(log_id,result)
    video_db.update_video_state(video_url, result)

@cel.task(queue='retry_queue')
def _try_video_again(video_url, username=''):
    encode_video_task(video_url, username)


