from bad_usernames import UNAVAILABLE_USERNAMES_LAST_UPDATED, UNAVAILABLE_USERNAMES

DEBUG = False

SECRET_KEY = 'franklySpeakingThisIsVeryConfidential'
MULTIPLE_AUTH_HEADERS = ['access_token', 'device']

PORT = 8000
PROPOGATE_EXCEPTIONS = True

RAYGUN_KEY = "7UhM72ttZSLGprISFjVg0Q=="

AWS_KEY = 'AKIAJ72DWIKVJZNTD2VA'
AWS_SECRET = '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' 

TWITTER_APP_TOKEN = 'aaNDJcxdHadQTxBW8P7B42yoy'
TWITTER_APP_SECRET = 'AAOwvDBHlci4WmJANTmgOLJg28v3HSx0SogBEfQY9TGamsF9CS'

REDIS_HOST = 'franklyapi.wocnxz.0001.use1.cache.amazonaws.com'

MYSQL_HOST = 'franklyapi.c0gm6ruawjoo.us-east-1.rds.amazonaws.com:3306'
MYSQL_USERNAME = 'franklyapi'
MYSQL_PASSWORD = 'Jack4Jill$'
MYSQL_DATABASE_NAME = 'frankly'

DATABASE_URI = 'mysql://{username}:{password}@{host}/{db_name}'.format(username=MYSQL_USERNAME, 
                                                                        password=MYSQL_PASSWORD, 
                                                                        host=MYSQL_HOST,
                                                                        db_name=MYSQL_DATABASE_NAME)

ASYNC_ENCODER_BROKER_URL = "redis://{redis_host}/8".format(redis_host=REDIS_HOST)
ASYNC_ENCODER_BACKEND_URL = "redis://{redis_host}/8".format(redis_host=REDIS_HOST)

ALLOWED_PICTURE_FORMATS = ['jpg', 'jpeg', 'png']
ALLOWED_VIDEO_FORMATS = ['mp4']
ALLOWED_AUDIO_FORMATS = ['mp3', 'ogg', 'wav', 'aac', '3gp']

BLOCKED_EMAIL_DOMAINS = ['mailinator.com']
ALLOWED_CHARACTERS = [ chr(item) for item in range(48,58)+range(65,91)+[95]+range(97,123)]

ADMIN_USERS = []