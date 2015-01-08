pimport sys
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
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.id in config.ADMIN_USERS:
            abort(403, message='Invalid Login')
        return f(*args, **kwargs)
    return decorated


class AdminProtectedResource(restful.Resource):
        method_decorators = [admin_only]



class AdminUserList(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('offset', type=int, default=0, location='args')
        arg_parser.add_argument('limit', type=int, default=10, location='args')
        arg_parser.add_argument('user_type', type=int, default=2, location='args')
        arg_parser.add_argument('deleted', type=int, default=0, location='args')
        arg_parser.add_argument('order_by', type=str, default='user_since', choices=['user_since', 'name'], location='args')
        arg_parser.add_argument('desc', type=int, default=1, choices=[1, 0], location='args')

        
        try:
            args = arg_parser.parse_args()
            return admin_controllers.user_list(offset=args['offset'],
                                                    limit=args['limit'],
                                                    user_type=bool(args['user_type']),
                                                    deleted=bool(args['deleted']),
                                                    order_by=args['order_by'],
                                                    desc=bool(args['desc'])
                                                    )
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))


class AdminUserAdd(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('email', type=str, required=True, location='forms')
        arg_parser.add_argument('username', type=str, required=True, location='forms')
        arg_parser.add_argument('first_name', type=str, required=True, location='forms')
        arg_parser.add_argument('bio', type=str, required=True, location='forms')
        arg_parser.add_argument('password', type=str, required=True, location='forms')
        arg_parser.add_argument('user_title', type=str, location='forms')
        arg_parser.add_argument('user_type', type=int, default=-1, choices=[-1, 0, 2], location='forms')
        arg_parser.add_argument('gender', type=str, choices=['M', 'F'], location='forms')

        arg_parser.add_argument('profile_picture', required=True, type=file, location='files')
        arg_parser.add_argument('profile_video', required=True, type=file, location='files')

        try:
            args = arg_parser.parse_args()
            return admin_controllers.user_add(email=args['email'],
                                                username=args['username'],
                                                first_name=args['first_name'],
                                                bio=args['bio'],
                                                password=args['password'],
                                                user_title=args['user_title'],
                                                user_type=args['user_type']
                                                gender=args['gender']
                                                profile_picture=args['profile_picture']
                                                profile_video=args['profile_video']
                                                )
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))


class AdminUserEdit(AdminProtectedResource):
    @login_required
    def get(self):

        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('user_id', type=str, required=True, location='forms')
        arg_parser.add_argument('email', type=str, location='forms')
        arg_parser.add_argument('username', type=str, location='forms')
        arg_parser.add_argument('first_name', type=str, location='forms')
        arg_parser.add_argument('bio', type=str, location='forms')
        arg_parser.add_argument('password', type=str, location='forms')
        arg_parser.add_argument('user_title', type=str, location='forms')
        arg_parser.add_argument('user_type', type=int, choices=[-1, 0, 2], location='forms')
        arg_parser.add_argument('gender', type=str, choices=['M', 'F'], location='forms')

        arg_parser.add_argument('profile_picture', type=file, location='files')
        arg_parser.add_argument('profile_video', type=file, location='files')

        try:
            args = arg_parser.parse_args()
            return admin_controllers.user_edit(user_id=args['user_id'],
                                                email=args['email'],
                                                username=args['username'],
                                                first_name=args['first_name'],
                                                bio=args['bio'],
                                                password=args['password'],
                                                user_title=args['user_title'],
                                                user_type=args['user_type'],
                                                profile_picture=args['profile_picture'],
                                                profile_video=args['profile_video'],
                                                deleted=args['deleted'],
                                                phone_num=args['phone_num'])
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))





class AdminQuestionList(AdminProtectedResource):
    @login_required
    def get(self):
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
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))



class AdminQuestionDelete(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        
        return admin_controllers.question_delete(question_id=args['question_id'])

class AdminQuestionUndelete(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        
        return admin_controllers.question_undelete(question_id=args['question_id'])

class AdminQuestionEdit(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        arg_parser.add_argument('body', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        
        return admin_controllers.question_edit(question_id=args['question_id'], body=args['body'])
