import video_encoder
from configs import config
from celery import Celery

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

@cel.task(queue='new_encoding')
def encode_video_task(video_url):
    import controllers
    result = video_encoder.encode_video(video_url)
    controllers.update_video_state(video_url, result)

@cel.task(queue='retry_queue')
def try_video_again(video_url):
    encode_video_task(video_url)