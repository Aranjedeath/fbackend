import sys
import traceback

from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask.ext.login import login_required, current_user
from raygun4py import raygunprovider

import CustomExceptions

from configs import config
from functools import wraps

import admin_controllers

def admin_only(f):
    try:
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.id in config.ADMIN_USERS:
                abort(403, message='Invalid Login')
            return f(*args, **kwargs)
    except Exception as e:
        print traceback.format_exc(e)
        raise e
    return decorated


class AdminProtectedResource(restful.Resource):
        method_decorators = [admin_only]


class AdminQuestionList(AdminProtectedResource):
    @login_required
    def get():
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('offset', type=int, default=0, location='args')
        arg_parser.add_argument('limit', type=int, default=10, location='args')
        arg_parser.add_argument('public', type=int, default=1, location='args')
        arg_parser.add_argument('deleted', type=int, default=0, location='args')
        try:

            args = arg_parser.parse_args()
        
            return admin_controllers.question_list(offset=args['offset'],
                                                    limit=args['limit'],
                                                    public=bool(args['public']),
                                                    deleted=bool(args['deleted'])
                                                    )
        except Exception as e:
            return traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))



class AdminQuestionDeleted(AdminProtectedResource):
    @login_required
    def get():
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=int, default=0, location='args')
        arg_parser.add_argument('limit', type=int, default=10, location='args')
        arg_parser.add_argument('public', type=int, default=1, location='args')
        arg_parser.add_argument('deleted', type=int, default=0, location='args')
        
        args = arg_parser.parse_args()
        
        return admin_controllers.question_list(offset=args['offset'],
                                        limit=args['limit'],
                                        public=args['public'],
                                        deleted=args['deleted']
                                        )



