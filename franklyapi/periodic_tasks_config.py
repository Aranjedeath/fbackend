from datetime import timedelta
from configs import config
import crontab as cron

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
    'task4': {
        'task': 'periodic_tasks.log_video_count',
        'schedule': cron(hour=23,minute=0),
        'options':{'queue': 'periodic'},
    },
    'task5': {
        'task': 'periodic_tasks.weekly_report',
        'schedule': cron(hour=8,minute=0,day_of_week='monday'),
        'options':{'queue': 'periodic'},

    },
    'task6': {
        'task': 'periodic_tasks.daily_report',
        'schedule': cron(hour=9,minute=0),
        'options':{'queue': 'periodic'},

    },
    'task7': {
        'task': 'periodic_tasks.twice_a_day_report',
        'schedule': cron(minute='*'),
        'options':{'queue': 'periodic'},

    }
}
