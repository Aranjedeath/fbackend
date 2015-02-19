from datetime import timedelta
from configs import config

BROKER_URL = config.ASYNC_ENCODER_BROKER_URL
CELERY_RESULT_BACKEND = config.ASYNC_ENCODER_BACKEND_URL

CELERYBEAT_SCHEDULE = {
    'task1': {
        'task': 'periodic_tasks.update_view_count',
        'schedule': timedelta(seconds=300),
        'options':{'queue': 'periodic'},
    },
    'task2': {
        'task': 'periodic_tasks.update_user_view_count',
        'schedule': timedelta(seconds=600),
        'options':{'queue': 'periodic'},
    },
    'task3': {
        'task': 'periodic_tasks.reassign_pending_video_tasks',
        'schedule': timedelta(seconds=3600),
        'options':{'queue': 'periodic'},
    },
}
