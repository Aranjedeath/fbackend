import sys
import traceback

from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask.ext.login import login_required, current_user

import CustomExceptions

from app import raygun

from configs import config
from functools import wraps

import admin_controllers

def admin_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user or not current_user.id in config.ADMIN_USERS:
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
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')


class AdminUserAdd(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('email', type=str, required=True, location='form')
        arg_parser.add_argument('username', type=str, required=True, location='form')
        arg_parser.add_argument('first_name', type=str, required=True, location='form')
        arg_parser.add_argument('bio', type=str, required=True, location='form')
        arg_parser.add_argument('password', type=str, required=True, location='form')
        arg_parser.add_argument('user_title', type=str, location='form')
        arg_parser.add_argument('user_type', type=int, default=-1, choices=[-1, 0, 2], location='form')
        arg_parser.add_argument('gender', type=str, choices=['M', 'F'], location='form')

        arg_parser.add_argument('profile_picture', type=file, location='files')
        arg_parser.add_argument('profile_video', type=file, location='files')
        args = arg_parser.parse_args()
        print 'bhonsdi wala.'

        try:
            return admin_controllers.user_add(email=args['email'],
                                                username=args['username'],
                                                first_name=args['first_name'],
                                                bio=args['bio'],
                                                password=args['password'],
                                                user_title=args['user_title'],
                                                user_type=args['user_type'],
                                                gender=args['gender'],
                                                profile_picture=args['profile_picture'],
                                                profile_video=args['profile_video']
                                                )
        except Exception as e:
            print 'Hellllllo'
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminPostEdit(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('post_id', type=str, required=True, location='form')
        arg_parser.add_argument('video', type=file, required=True, location='files')
        args = arg_parser.parse_args()
        try:
            return admin_controllers.post_edit(post_id=args['post_id'],
                                                video=args['video'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminUserEdit(AdminProtectedResource):
    @login_required
    def post(self):

        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('user_id', type=str, required=True, location='json')
        arg_parser.add_argument('email', type=str, location='json')
        arg_parser.add_argument('username', type=str, location='json')
        arg_parser.add_argument('first_name', type=str, location='json')
        arg_parser.add_argument('bio', type=str, location='json')
        arg_parser.add_argument('password', type=str, location='json')
        arg_parser.add_argument('user_title', type=str, location='json')
        arg_parser.add_argument('user_type', type=int, choices=[-1, 0, 2], location='json')
        arg_parser.add_argument('gender', type=str, choices=['M', 'F'], location='json')

        arg_parser.add_argument('profile_picture', type=file, location='files')
        arg_parser.add_argument('profile_video', type=file, location='files')
        args = arg_parser.parse_args()

        try:
            return admin_controllers.user_edit(user_id=args['user_id'],
                                                email=args['email'],
                                                username=args['username'],
                                                first_name=args['first_name'],
                                                bio=args['bio'],
                                                password=args['password'],
                                                user_title=args['user_title'],
                                                user_type=args['user_type'],
                                                profile_picture=args['profile_picture'],
                                                profile_video=args['profile_video'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')





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
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')


class AdminQuestionAdd(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_to', type=str,location = 'json', required = True)
        arg_parser.add_argument('question_author', type=str,location = 'json', default = None)
        arg_parser.add_argument('question_body', type=str,location = 'json', required = True)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.question_add(args['question_to'], args['question_body'], args['question_author'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')



class AdminQuestionDelete(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        try:
            return admin_controllers.question_delete(question_id=args['question_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminQuestionUndelete(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        try:
            return admin_controllers.question_undelete(question_id=args['question_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminQuestionEdit(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id', type=str, default=0, location='json')
        arg_parser.add_argument('body', type=str, default=0, location='json')
        args = arg_parser.parse_args()
        try:
            return admin_controllers.question_edit(question_id=args['question_id'], body=args['body'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminAddCelebQue(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('item_id', type= str, location = 'json', required = True)
        arg_parser.add_argument('item_type', type=str, location = 'json', required = True, choices = ['user', 'post', 'question'])
        arg_parser.add_argument('item_day', type=str, location = 'json', required = True)
        arg_parser.add_argument('item_score', type=str, location = 'json', required = True)

        args = arg_parser.parse_args()
        try:
            return admin_controllers.add_celeb_in_queue(args['item_id'], args['item_type'], args['item_day'], args['item_score'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminQueOrderEdit(AdminProtectedResource):
    @login_required
    def get(self):
        try:
            return admin_controllers.get_que_order()
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

    @login_required
    def post(self):
        from flask import request
        print request.json

        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('items', type=list, location='json', required = True)
        args = arg_parser.parse_args()
        print args
        try:
            return admin_controllers.update_que_order(args['items'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminCelebList(AdminProtectedResource):
    @login_required
    def get(self,offset, limit):
        try:
            return admin_controllers.get_celeb_list(offset, limit)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminCelebSearch(AdminProtectedResource):
    @login_required
    def get(self,query):
        try:
            return admin_controllers.get_celeb_search(query)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminQueueDelete(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('item_type', type=str, location='json', required = True, choices=['post', 'user', 'question'])
        arg_parser.add_argument('item_id', type=str, location='json', required = True)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.delete_from_central_queue(args['item_type'], args['item_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminCelebsAskedToday(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('offset', type=int, location='args', default=0)
        arg_parser.add_argument('limit', type=int, location='args', default=10)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.get_celebs_asked_today(args['offset'], args['limit'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminQuestionTodayList(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('user_id', type=str, location='args', required=True)
        arg_parser.add_argument('offset', type=int, location='args', default=0)
        arg_parser.add_argument('limit', type=int, location='args', default=10)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.get_questions_asked_today(args['user_id'], args['offset'], args['limit'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminDeleteSearchDefaultUser(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('category_name', type=str, required=True, location='json')
        arg_parser.add_argument('user_id', type=str, required = True, location = 'json')
        args = arg_parser.parse_args()

        try:
            return admin_controllers.delete_search_default_user(args['category_name'], args['user_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminUpdateSearchDefaultCategoryOrder(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('category_name', type=str, required=True, location='json')
        arg_parser.add_argument('cat_user_data', type=list, required = True, location = 'json')
        args = arg_parser.parse_args()

        try:
            return admin_controllers.update_category_order_search_default(args['category_name'], args['cat_user_data'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')
        
class AdminRedirectQuestion(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('primary_question_id', type=str, required=True, location='json')
        arg_parser.add_argument('questions_to_redirect', type=list, required = True, location = 'json')
        args = arg_parser.parse_args()

        try:
            return admin_controllers.questions_redirect(args['primary_question_id'], args['questions_to_redirect'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminGetUnansweredQuestionListWithSameCount(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('user_id', type=str, required = True, location = 'args')
        arg_parser.add_argument('offset', type=int, default=0, location = 'args')
        arg_parser.add_argument('limit', type=int, default=5, location = 'args')
        args = arg_parser.parse_args()
        print args

        try:
            return admin_controllers.get_unanswered_questions_with_same_count(args['user_id'], args['offset'], args['limit'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminGetSimilarQuestions(AdminProtectedResource):
    @login_required
    def get(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('question_id',required=True, location='args', type=str)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.get_similar_questions(args['question_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminGetDateFeed(AdminProtectedResource):
    @login_required
    def get(self):
        try:
            return admin_controllers.get_date_sorted_list()
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminAddToDateFeed(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('type',type=str, choices=['user','post'], required=True)
        arg_parser.add_argument('obj_id',type=str,  required=True)
        arg_parser.add_argument('timestamp',type=int,  required=True)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.add_to_date_sorted(args['type'], args['obj_id'], args['timestamp'])
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminDeleteFromDateFeed(AdminProtectedResource):
    @login_required
    def post(self):
        arg_parser = reqparse.RequestParser()
        arg_parser.add_argument('type',type=str, choices=['user','post'], required=True)
        arg_parser.add_argument('obj_id',type=str,  required=True)
        args = arg_parser.parse_args()
        try:
            return admin_controllers.delete_date_sorted_item(args['type'],args['obj_id'])
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message='Error')

class AdminUpdateDateFeedOrder(AdminProtectedResource):
    @login_required
    def post(self):
        from flask import request
        print request.json
        try:
            return admin_controllers.update_date_feed_order(request.json['date'], request.json['items'])
        except Exception as e:
            print traceback.format_exc(e)
            abort(500, message='Error')
