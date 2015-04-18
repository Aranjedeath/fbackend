import sys
import traceback
import media_uploader
import video_encoder
from configs import config
from celery import Celery
from notification import notification_decision
import video_db
from app import db, raygun

cel = Celery(broker=config.ASYNC_ENCODER_BROKER_URL, backend=config.ASYNC_ENCODER_BACKEND_URL)

default_queues = {}
for item, data in video_encoder.VIDEO_ENCODING_PROFILES.items():
    default_queues[item] = data['default_queue']


@cel.task(queue='encoding')
def encode_video_task(video_url, username='', profiles=video_encoder.VIDEO_ENCODING_PROFILES.keys(), queues={}, redo=False):
    default_queue = default_queues.copy()
    for profile, queue in queues.items():
        default_queue['item'] = queue

    file_path = None
    for profile_name in profiles:
        if redo or not video_db.video_already_encoded(video_url=video_url, video_quality=profile_name, recent_assigned=True):
            if not file_path:
                file_path = media_uploader.download_file(video_url)
            log_id = video_db.add_video_encode_log_start(video_url=video_url, video_quality=profile_name)
            if redo:
                _try_video_again(video_url, username, profiles)

            _encode_video_to_profile.apply_async(kwargs={'file_path': file_path,
                                                         'video_url': video_url,
                                                         'profile': profile_name,
                                                         'log_id': log_id,
                                                         'username': username
                                                         },
                                                 queue=default_queue[profile_name]
                                                 )
        else:
            print 'Already Done'
    db.engine.dispose()


@cel.task(queue='encoding_low_priority')
def _encode_video_to_profile(file_path, video_url, profile, log_id, username=''):
    if video_db.video_already_encoded(video_url=video_url, video_quality=profile):
        print 'Not Retrying now.'
        return
    result = video_encoder.encode_video_to_profile(file_path, video_url, profile, username)
    video_db.update_video_encode_log_finish(log_id, result)
    video_db.update_video_state(video_url, result)

    #if low was not made make try for medium
    if profile == 'low' and not result:
        log_id = video_db.add_video_encode_log_start(video_url=video_url, video_quality='medium')
        _encode_video_to_profile(file_path, video_url, 'medium', log_id, username=username)

    if result:
        try:
            post_id = video_db.get_post_id_from_video(video_url)
            if post_id:
                notification_decision.post_notifications(post_id)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
    db.engine.dispose()


@cel.task(queue='encoding_retry')
def _try_video_again(video_url, username='', profiles=video_encoder.VIDEO_ENCODING_PROFILES.keys()):
    encode_video_task(video_url, username, profiles, queues=dict(promo='encoding_low_priority', opt='encoding_retry', ultralow='encoding_retry', low='encoding_retry', medium='encoding_retry'))
