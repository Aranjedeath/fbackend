DEBUG = False

SECRET_KEY = 'franklySpeakingThisIsVeryConfidential'
MULTIPLE_AUTH_HEADERS = ['access_token', 'device']

PORT = 8000
PROPOGATE_EXCEPTIONS = True

RAYGUN_KEY = "7UhM72ttZSLGprISFjVg0Q=="

AWS_KEY = 'AKIAJ72DWIKVJZNTD2VA'
AWS_SECRET_KEY = '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' 

REDIS_HOST = 'franklyapi.wocnxz.0001.use1.cache.amazonaws.com'

MYSQL_HOST = 'franklyapi.c0gm6ruawjoo.us-east-1.rds.amazonaws.com:3306'
MYSQL_USERNAME = 'franklyapi'
MYSQL_PASSWORD = 'Jack4Jill$'
MYSQL_DATABASE_NAME = 'frankly'

DATABASE_URI = 'mysql://{username}:{password}@{host}/{db_name}'.format(username=MYSQL_USERNAME, 
                                                                        password=MYSQL_PASSWORD, 
                                                                        host=MYSQL_HOST,
                                                                        db_name=MYSQL_DATABASE_NAME)