import video_encoder
import media_uploader
from configs import config
from celery import Celery
import video_db

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

@cel.task(queue='new_encoding')
def encode_video_task(video_url, username=''):
    video_db.add_video_to_db(video_url)
    file_path = media_uploader.download_file(video_url)

    for profile_name in video_encoder.VIDEO_ENCODING_PROFILES.keys():
        _encode_video_to_profile(file_path, video_url, profile_name, username)    


@cel.task(queue='new_encoding')
def _encode_video_to_profile(file_path, video_url, profile, username=''):
    result = video_encoder.encode_video_to_profile(file_path, video_url, profile, username)
    video_db.update_video_state(video_url, result)


@cel.task(queue='retry_queue')
def _try_video_again(video_url, username=''):
    encode_video_task(video_url, username)
