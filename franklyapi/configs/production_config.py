from bad_usernames import UNAVAILABLE_USERNAMES_LAST_UPDATED, UNAVAILABLE_USERNAMES
import socket

DEBUG = False

SECRET_KEY = 'franklySpeakingThisIsVeryConfidential'
MULTIPLE_AUTH_HEADERS = ['access_token', 'device']

PORT = 8000
PROPOGATE_EXCEPTIONS = True

RAYGUN_KEY = "hAmfuTIzQ8jYdMiQdh1fug=="

#Raygun username and password is used for documentation
RAYGUN_USERNAME = "frankly1@mailinator.com" 
RAYGUN_PASSWORD = "dexter123"

AWS_KEY = 'AKIAJ72DWIKVJZNTD2VA'
AWS_SECRET = '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' 

TWITTER_APP_TOKEN = 'aaNDJcxdHadQTxBW8P7B42yoy'
TWITTER_APP_SECRET = 'AAOwvDBHlci4WmJANTmgOLJg28v3HSx0SogBEfQY9TGamsF9CS'

REDIS_HOST = 'redis-cache-cluster.o5tg28.0001.apse1.cache.amazonaws.com'

MYSQL_HOST = 'franklyapi.ce1zyhcvu8o4.ap-southeast-1.rds.amazonaws.com:3306'
#MYSQL_USERNAME = 'application_user'
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

ADMIN_USERS = ['cab4132c53c6b197df310373dba38e5f','cab4132c53c6a513df310374a482ef4e','cab4132c53c6a447df3103743a3fabdf']
TEST_USERS = []

SPREADSHEET_EMAIL = 'tempuser@frankly.me'
SPREADSHEET_PASSWORD = 'franklydocs'

DEFAULT_BIO = "Ask me anything for video replies."

GCM_API_KEY = 'AIzaSyBKa5pjzTdbdLwMcYkic1yK1q_fbHljbxY'

WEB_URL = 'http://frankly.me'

HOSTNAME = socket.gethostname()

GCM_API_KEY = 'AIzaSyBKa5pjzTdbdLwMcYkic1yK1q_fbHljbxY'

ANDROID_APPSTORE_LINK = 'https://play.google.com/store/apps/details?id=me.frankly'
IOS_APPSTORE_LINK = 'https://itunes.apple.com/in/app/frankly.me-talk-to-celebrities/id929968427'

ANDROID_LATEST_VERSION_CODE = 42
ANDROID_NECESSARY_VERSION_CODE = 40
IOS_LATEST_VERSION_CODE = 42
IOS_NECESSARY_VERSION_CODE = 41
