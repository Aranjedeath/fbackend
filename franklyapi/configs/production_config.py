from bad_usernames import UNAVAILABLE_USERNAMES_LAST_UPDATED, UNAVAILABLE_USERNAMES

DEBUG = False

SECRET_KEY = 'franklySpeakingThisIsVeryConfid'
MULTIPLE_AUTH_HEADERS = ['access_token', 'device']

PORT = 8000
PROPOGATE_EXCEPTIONS = True

RAYGUN_KEY = ""

AWS_KEY = ''
AWS_SECRET = '' 

TWITTER_APP_TOKEN = ''
TWITTER_APP_SECRET = ''

REDIS_HOST = ''

MYSQL_HOST = ''
MYSQL_USERNAME = ''
MYSQL_PASSWORD = ''
MYSQL_DATABASE_NAME = ''

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

ADMIN_USERS = [] #user_id

SPREADSHEET_EMAIL = ''
SPREADSHEET_PASSWORD = ''


