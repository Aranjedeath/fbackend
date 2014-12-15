import redis

from flask import Flask
from flask.ext import restful
from flask.ext.login import LoginManager
from raygun4py import raygunprovider
from flask.ext.sqlalchemy import SQLAlchemy

from configs import config

class FlaskConfig():
    DEBUG = config.DEBUG
    SECRET_KEY = config.SECRET_KEY
    MULTIPLE_AUTH_HEADERS = config.MULTIPLE_AUTH_HEADERS
    PORT = config.PORT
    PROPOGATE_EXCEPTIONS = config.PROPOGATE_EXCEPTIONS
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI


appf = Flask(__name__)

appf.config.from_object(FlaskConfig)

login_manager = LoginManager()
login_manager.init_app(appf)

dbs = SQLAlchemy(appf)
api = restful.Api(appf)

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)
redis_client = redis.Redis(config.REDIS_HOST)

login_manager.login_view = '/login/email'

@appf.after_request
def add_access_control_headers(response):
    """Adds the required access control headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-Token, X-Deviceid,Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE'
    response.headers['Cache-Control'] = 'No-Cache'
    response.headers['X-Server'] = 'api.frankly.me'
    return response

@login_manager.multiple_headers_loader
def load_header(header_vals):
    from controllers import check_access_token
    access_token, device_id = header_vals.get('X-Token'), header_vals.get('X-Deviceid')
    if not (access_token and device_id):
        return None
    return check_access_token(access_token, device_id)



