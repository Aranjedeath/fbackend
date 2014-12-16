import video_encoder
import media_uploader
from configs import config
from celery import Celery


cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

@cel.task(queue='new_encoding')
def encode_video_task(video_url, thumbnail_url):
    import controllers
    controllers.add_video_to_db(video_url, thumbnail_url)
    file_path = media_uploader.download_file(video_url)
    for profile_name in video_encoder.VIDEO_ENCODING_PROFILES.keys():
        _encode_video_to_profile.delay(file_path, video_url, profile_name)    


@cel.task(queue='new_encoding')
def _encode_video_to_profile(file_path, video_url, profile):
    import controllers
    result = video_encoder.encode_video_to_profile(file_path, video_url, profile)
    controllers.update_video_state(video_url, result)


@cel.task(queue='retry_queue')
def _try_video_again(video_url, thumbnail_url):
    encode_video_task(video_url, thumbnail_url)