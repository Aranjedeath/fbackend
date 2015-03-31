import redis
import json
import traceback

from flask import Flask,request,g
from flask.ext import restful
from flask.ext.login import LoginManager
from raygun4py import raygunprovider
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from configs import config
from mailwrapper import SimpleMailer

class FlaskConfig():
    DEBUG = config.DEBUG
    SECRET_KEY = config.SECRET_KEY
    MULTIPLE_AUTH_HEADERS = config.MULTIPLE_AUTH_HEADERS
    PORT = config.PORT
    PROPOGATE_EXCEPTIONS = config.PROPOGATE_EXCEPTIONS
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URI


app = Flask(__name__)

app.config.from_object(FlaskConfig)

login_manager = LoginManager()
login_manager.init_app(app)


db = SQLAlchemy(app, session_options={'expire_on_commit': False})
api = restful.Api(app)


raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)
redis_client = redis.Redis(config.REDIS_HOST)
redis_views = redis.Redis(config.REDIS_HOST, db=7)
redis_search = redis.Redis(config.REDIS_HOST, db=4)
redis_pending_post = redis.Redis(config.REDIS_HOST, db=2)
redis_rate_limit = redis.Redis(config.REDIS_HOST, db=3)

login_manager.login_view = '/login/email'

time_log_file_name = "/tmp/flask-timelog.txt"


def log_to_time_log(response_time,request,response):
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    f=open(time_log_file_name, 'a')
    try:
        now = datetime.now()
        now_string = now.strftime(datetime_format)
        log_string = ' :: '.join([str(response_time),  response.status, request.url, json.dumps(request.args), now_string]) + '\n'
        f.write(log_string)
        print log_string
        pass
    except Exception, e:
        print traceback.format_exc(e)
    f.close()
@app.before_request
def add_begin_time_to_g():
    g.begin_time = datetime.now()

@app.after_request
def add_access_control_headers(response):
    import json
    """Adds the required access control headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-Token, X-Deviceid,Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE'
    response.headers['Cache-Control'] = 'No-Cache'
    response.headers['X-Server'] = 'api.frankly.me'
    if 'dev' in config.HOSTNAME:
        try:
            data = json.loads(response.data)
            data['abra'] = 'kadabra'
            response.set_data(json.dumps(data))
        except Exception as e:
            print e

    now = datetime.now()
    diff = now - g.begin_time
    
    log_to_time_log(diff,request,response)

    return response

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


@login_manager.multiple_headers_loader
def load_header(header_vals):
    from controllers import check_access_token
    access_token, device_id = header_vals.get('X-Token'), header_vals.get('X-Deviceid')
    if not (access_token and device_id):
        return None
    return check_access_token(access_token, device_id)
