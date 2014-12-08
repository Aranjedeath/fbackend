import sys
import traceback
import redis

from flask import Flask
from flask.ext import restful
from flask.ext.login import LoginManager
from models import User, AccessToken
from database import engine, db_session
from sqlalchemy.sql import text
from raygun4py import raygunprovider


from configs import config

class FlaskConfig():
    DEBUG = config.DEBUG
    SECRET_KEY = config.SECRET_KEY
    MULTIPLE_AUTH_HEADERS = config.MULTIPLE_AUTH_HEADERS
    PORT = config.PORT
    PROPOGATE_EXCEPTIONS = config.PROPOGATE_EXCEPTIONS


app = Flask(__name__)

app.config.from_object(FlaskConfig)

login_manager = LoginManager()
login_manager.init_app(app)

api = restful.Api(app)

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)
redis_client = redis.Redis(config.REDIS_HOST)

ADMIN_USERS = []


login_manager.login_view = '/login/email'

@login_manager.multiple_headers_loader
def load_header(header_vals):
    try:
        access_token, device_id = header_vals.get('X-Token'), header_vals.get('X-Deviceid')
        if not access_token:
            return None
            
        user_id = None
        if device_id == 'web':
            device_type = 'web'
            user_id = redis_client.get(access_token)
            return User.query.get(int(user_id)) if user_id else None

        result = engine.execute(text("""SELECT user from access_tokens 
                                        where access_token=:access_token LIMIT 1"""), **{'access_token':access_token})

        row = result.fetchone()
        if row:
            user_id = int(row[0])
            redis_client.delete(access_token)

        else:
            user_id = redis_client.get(access_token)
            if user_id:
                device_type = 'ios' if len(device_id) > 16 else 'android'
                token_query = AccessToken.query.filter(AccessToken.device_id==device_id)
                if token_query.count():
                    AccessToken.query.filter(device_id=device_id
                                            ).update({ 'user':int(user_id), 'access_token':access_token})
                else:
                    db_session.add(AccessToken(device_id=device_id, user=int(user_id), 
                                access_token=access_token, device_type=device_type))
                    db_session.commit()

        if user_id:
            user = User.query.get(int(user_id))
            if user.deleted == True:
                return user
        return None
    except Exception as e:
        err = sys.exc_info()
        raygun.send(err[0],err[1],err[2])
        print traceback.format_exc(e)
        raise e




@app.after_request
def add_access_control_headers(response):
    """Adds the required access control headers"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-Token, X-Deviceid,Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST,GET,PUT,DELETE'
    response.headers['Cache-Control'] = 'No-Cache'
    response.headers['X-Server'] = 'api.frankly.me'
    return response



