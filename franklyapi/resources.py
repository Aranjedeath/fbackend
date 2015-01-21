import sys
import traceback

from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask.ext.login import login_required, current_user
from raygun4py import raygunprovider

import controllers
import CustomExceptions

from configs import config

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)

ALLOWED_PICTURE_FORMATS = ['jpg', 'jpeg']
ALLOWED_VIDEO_FORMATS = ['mp4']



class RegisterEmail(restful.Resource):
    def post(self):
        new_email_reg_parser = reqparse.RequestParser()
        new_email_reg_parser.add_argument('password', type=str, required=True, location='json')
        new_email_reg_parser.add_argument('email', type=str, required=True, location='json')
        new_email_reg_parser.add_argument('device_id', type=str, required=True, location='json')
        new_email_reg_parser.add_argument('full_name', type=str, required=True, location='json')
        new_email_reg_parser.add_argument('username', type=str, location='json', default = None)
        new_email_reg_parser.add_argument('web', type=bool, location='json', default=False)

        new_email_reg_parser.add_argument('gender', default='M', type=str, location='json', choices=['M', 'F'])
        new_email_reg_parser.add_argument('user_type', type=int, location='json', default = 0)

        new_email_reg_parser.add_argument('lat', default=None, type=str, location='json')
        new_email_reg_parser.add_argument('lon', default=None, type=str, location='json')
        new_email_reg_parser.add_argument('location_name', default=None, type=str, location='json')
        new_email_reg_parser.add_argument('country_name', default=None, type=str, location='json')
        new_email_reg_parser.add_argument('country_code', default=None, type=str, location='json')

        new_email_reg_parser.add_argument('phone_num', type=str, location='json')
        new_email_reg_parser.add_argument('push_id', type=str, location='json')
        args = new_email_reg_parser.parse_args()
        try:
            return controllers.register_email_user(  email=args['email'],
                                                    password=args['password'],
                                                    full_name=args['full_name'],
                                                    device_id=args.get('device_id'),
                                                    push_id=args.get('push_id'),
                                                    phone_num=args.get('phone_num'),
                                                    username=args.get('username'),
                                                    gender=args.get('gender'),
                                                    user_type=args['user_type'],
                                                    user_title=args.get('user_title'),
                                                    lat=args['lat'],
                                                    lon=args['lon'],
                                                    location_name=args['location_name'],
                                                    country_name=args['country_name'],
                                                    country_code=args['country_code']
                                                )
        except CustomExceptions.UserAlreadyExistsException as e:
            abort(409, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))

class LoginSocial(restful.Resource):
    def post(self, login_type):
        new_social_parser = reqparse.RequestParser()
        new_social_parser.add_argument('device_id', type=str, required=True, location='json')
        new_social_parser.add_argument('external_access_token', type=str, location='json', required=True)
        new_social_parser.add_argument('external_token_secret', type = str, location = 'json')
        new_social_parser.add_argument('social_user_id', type=str, location='json', required=True)
        new_social_parser.add_argument('push_id', type=str, location='json')
        new_social_parser.add_argument('user_type', type=int, location='json', default=1)
        new_social_parser.add_argument('user_title', type=str, location='json', default=None)
        args = new_social_parser.parse_args()
        try:
            if login_type not in ['google', 'facebook', 'twitter']:
                abort(404, message='Not Found')
            if login_type == 'twitter' and not args.get('external_token_secret'):
                abort(400, message='external_token_secret is a required Field')
            
            return controllers.login_user_social(social_type=login_type,
                                                 social_id=args['social_user_id'],
                                                 external_access_token=args['external_access_token'],
                                                 device_id=args['device_id'],
                                                 push_id=args.get('push_id'),
                                                 external_token_secret=args.get('external_token_secret'),
                                                 user_type=args.get('user_type'),
                                                 user_title=args.get('user_title')
                                                 )
        
        except CustomExceptions.InvalidTokenException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))


class LoginEmail(restful.Resource):
    def get(self):
        abort(403, message='Your Accesstoken has expired, Please login again')


    def post(self):
        new_email_login_parser = reqparse.RequestParser()
        new_email_login_parser.add_argument('username', type=str, required=True, location='json')
        new_email_login_parser.add_argument('password', type=str, required=True, location='json')
        new_email_login_parser.add_argument('device_id', type=str, required=True, location='json')
        new_email_login_parser.add_argument('push_id', type=str, location='json', default=None)
        args = new_email_login_parser.parse_args()
        try:
            if '@' in args['username'] and '.' in args['username']:
                id_type = 'email'
            else:
                id_type = 'username'
            return controllers.login_email_new( user_id = args['username'],
                                                id_type = id_type, 
                                                password = args['password'],
                                                device_id = args['device_id'],
                                                push_id = args['push_id']
                                                )
        except CustomExceptions.UserNotFoundException as e:
            print traceback.format_exc(e)
            abort(403, message='Wrong username/email or password')
        except CustomExceptions.PasswordMismatchException as e:
            print traceback.format_exc(e)
            abort(403, message='Wrong username/email or password')
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=traceback.format_exc(e))



class UserProfile(restful.Resource):

    def get(self, user_id):
        try:
            username = None
            if len(user_id)<32 and not user_id == 'me':
                username = user_id
                user_id = None

            if current_user.is_authenticated():
                if user_id == 'me':
                    user_id = current_user.id
                user_profile = controllers.user_view_profile(current_user.id, user_id, username=username)
            else:
                if user_id == 'me':
                    abort(404, message='User Not Found')
                user_profile = controllers.user_view_profile(None, user_id, username=username)

            return user_profile

        except CustomExceptions.UserNotFoundException, e:
            print traceback.format_exc(e)
            abort(404, message='User Not Found')
        except CustomExceptions.BlockedUserException as e:
            print traceback.format_exc(e)
            abort(404, message="User Not found")
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserUpdateForm(restful.Resource):
    @login_required
    def post(self, user_id):

        user_update_profile_form = reqparse.RequestParser()
        user_update_profile_form.add_argument('first_name', type=str, location='form')
        user_update_profile_form.add_argument('bio', type=str, location='form')
        user_update_profile_form.add_argument('user_title', type=str, location='form')
        user_update_profile_form.add_argument('profile_picture', location='files')
        user_update_profile_form.add_argument('profile_video', location='files')
        args = user_update_profile_form.parse_args()
        print args
               
        try:
            if user_id == 'me':
                user_id = current_user.id
            
            if (current_user.id not in config.ADMIN_USERS) and user_id != current_user.id:
                raise CustomExceptions.BadRequestException()
            if current_user.id not in config.ADMIN_USERS:
                args['user_title'] = None
            
            new_profile = controllers.user_update_profile_form(user_id,
                                                                first_name=args['first_name'],
                                                                bio=args['bio'],
                                                                user_title=args['user_title'],
                                                                profile_picture=args['profile_picture'],
                                                                profile_video=args['profile_video'])
            return new_profile

        except CustomExceptions.BadRequestException, e:
            print traceback.format_exc(e)
            abort(400, message=str(e))

        except Exception as e:
            print traceback.format_exc(e)
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            abort(500, message="Internal Server Error")


class UserProfileUsername(restful.Resource):
    def get(self, username):
        try:
            user_profile = controllers.user_view_profile(current_user.id, user_id=None, username=username)
            return user_profile

        except CustomExceptions.UserNotFoundException, e:
            print traceback.format_exc(e)
            abort(404, message='User Not Found')
        except CustomExceptions.BlockedUserException as e:
            print traceback.format_exc(e)
            abort(404, message="User Not found")
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserFollow(restful.Resource):
    @login_required
    def post(self):
        
        user_follow_parser = reqparse.RequestParser()
        user_follow_parser.add_argument('user_id', required=True, type=str, location='json')
        args = user_follow_parser.parse_args()
        
        try:
            resp = controllers.user_follow(current_user.id, user_id=args['user_id'])
            return resp

        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserUnfollow(restful.Resource):
    @login_required
    def post(self):
        
        user_unfollow_parser = reqparse.RequestParser()
        user_unfollow_parser.add_argument('user_id', required=True, type=str, location='json')
        args = user_unfollow_parser.parse_args()
        
        try:
            resp = controllers.user_unfollow(current_user.id, user_id=args['user_id'])
            return resp

        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserFollowers(restful.Resource):
    def get(self, user_id):
        
        username=None

        if current_user.is_authenticated():
            current_user_id = current_user.id
        else:
            current_user_id = None

        if user_id == 'me':
            user_id = current_user_id
        elif len(user_id) < 32:
            username = user_id

        user_followers_parser = reqparse.RequestParser()
        user_followers_parser.add_argument('offset', default=0, type=int, location='args')
        user_followers_parser.add_argument('limit', default=10, type=int, location='args')
        args = user_followers_parser.parse_args()
        
        try:
            if not user_id:
                raise CustomExceptions.UserNotFoundException('You need to login to view this.')
            resp = controllers.user_followers(current_user_id,
                                                user_id=user_id, 
                                                username=username,
                                                offset=args['offset'],
                                                limit=args['limit'])
            return resp

        except CustomExceptions.UserNotFoundException as e:
            abort(404, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserBlock(restful.Resource):
    @login_required
    def post(self):
        user_block_parser = reqparse.RequestParser()
        user_block_parser.add_argument('user_id', required=True, type=str, location='json')
        args = user_block_parser.parse_args()
        
        try:
            resp = controllers.user_block(current_user.id, user_id=args['user_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Error")


class UserUnblock(restful.Resource):
    @login_required
    def post(self):
        user_unblock_parser = reqparse.RequestParser()
        user_unblock_parser.add_argument('user_id', required=True, type=str, location='json')
        args = user_unblock_parser.parse_args()
        
        try:
            resp = controllers.user_unblock(current_user.id, user_id=args['user_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Error")


class UserBlockList(restful.Resource):

    @login_required
    def get(self):
        try:
            resp = controllers.user_block_list(current_user.id)
            return resp
        
        except CustomExceptions.BadRequestException as e:
            print traceback.format_exc(e)
            abort(400, message="Bad Request")
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)


class ChangeUsername(restful.Resource):
    @login_required
    def post(self):
        user_change_username_parser = reqparse.RequestParser()
        user_change_username_parser.add_argument('username', required=True, type=str, location='json')
        user_change_username_parser.add_argument('id', type=str, location='json')
        args = user_change_username_parser.parse_args()
        
        try:
            if current_user.id in config.ADMIN_USERS:
                user_id = args['id']
            else:
                user_id = current_user.id
            resp = controllers.user_change_username(user_id, new_username=args['username'])
            return resp

        except CustomExceptions.UnameUnavailableException, e:
            abort(409, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class ChangePassword(restful.Resource):
    @login_required
    def post(self):
        user_change_password_parser = reqparse.RequestParser()
        user_change_password_parser.add_argument('password', required=True, type=str, location='json')
        args = user_change_password_parser.parse_args()
        try:
            resp = controllers.user_change_password(current_user.id, new_password=args['password'])
            return resp

        except CustomExceptions.UnameUnavailableException, e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserExists(restful.Resource):

    def post(self):
        user_exist_parser = reqparse.RequestParser()
        user_exist_parser.add_argument('username', type=str, location='json', default=None)
        user_exist_parser.add_argument('email', type=str, location='json', default=None)
        user_exist_parser.add_argument('phone_number', type=str, location='json', default=None)
        args = user_exist_parser.parse_args()
        try:
            resp = controllers.user_exists(username=args['username'], email=args['email'], phone_number=args['phone_number'])
            return resp
        except CustomExceptions.BadRequestException as e:
            print traceback.format_exc(e)
            abort(400, message="Bad Request")



class UserSettings(restful.Resource):
    @login_required
    def get(self):
        try:
            resp = controllers.user_get_settings(current_user.id)
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)


    @login_required
    def post(self):
        user_setting_parser = reqparse.RequestParser()
        user_setting_parser.add_argument('allow_anonymous_question', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_like', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_follow', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_question', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_comments', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_mention', type=bool, location='json', required=True)
        user_setting_parser.add_argument('notify_answer', type=bool, location='json', required=True)
        user_setting_parser.add_argument('timezone', type=int, location='json', default=0)
        args = user_setting_parser.parse_args()
        
        try:
            controllers.user_update_settings(current_user.id, 
                                            allow_anonymous_question=args['allow_anonymous_question'],
                                            notify_like=args['notify_like'],
                                            notify_follow=args['notify_follow'],
                                            notify_question=args['notify_question'],
                                            notify_comments=args['notify_comments'],
                                            notify_mention=args['notify_mention'],
                                            notify_answer=args['notify_answer'],
                                            timezone=args['timezone']
                                                    )
            return args
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)


class UserLocation(restful.Resource):

    def post(self):
        update_location_parser = reqparse.RequestParser()
        update_location_parser.add_argument('coordinate_point' , required=True, location='json', type=list)
        update_location_parser.add_argument('country' , location='json', type=str, default=None)
        update_location_parser.add_argument('country_code' , location='json', type=str, default=None)
        update_location_parser.add_argument('loc_name' , location='json', type=str, default=None)
        args = update_location_parser.parse_args()
        
        try:
            return {'success' : True}
            controllers.user_update_location(user_id = current_user.id,
                                            lon = args['coordinate_point'][0],
                                            lat = args['coordinate_point'][1],
                                            country = args['country'],
                                            country_code = args['country_code'],
                                            loc_name = args['loc_name']
                                            )
            return {'success' : True}

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UpdatePushId(restful.Resource):
    @login_required
    def post(self):
        update_push_id_parser = reqparse.RequestParser()
        update_push_id_parser.add_argument('X-Deviceid', type=str, required=True, location = 'headers', dest='device_id')
        update_push_id_parser.add_argument('push_id', type=str, location='json', required=True)
        args = update_push_id_parser.parse_args()
        try:
            controllers.update_push_id(current_user.id, device_id=args['device_id'], push_id=args['push_id'])
            return {'success' : True}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Internal Server Error')

class UserUpdateToken(restful.Resource):
    @login_required
    def post(self):
        user_update_token = reqparse.RequestParser()
        user_update_token.add_argument('acc_type', type=str, location='json', default='facebook', choices=['facebook'])
        user_update_token.add_argument('token', type=str, location='json', required=True)
        args = user_update_token.parse_args()
        try:
            resp = controllers.user_update_access_token(current_user.id, acc_type=args['acc_type'], token=args['token'])
            return resp

        except CustomExceptions.BadRequestException as e:
            print traceback.format_exc(e)
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class QuestionAsk(restful.Resource):
    @login_required
    def post(self):
        ask_parser = reqparse.RequestParser()
        ask_parser.add_argument('question_to', type=str, required=True, location='json')
        ask_parser.add_argument('body', type=str, required=True, location='json')
        ask_parser.add_argument('coordinate_point', type=list, default=[None, None], location='json')
        ask_parser.add_argument('is_anonymous', type=bool, required=True, location='json')
        args = ask_parser.parse_args()
        
        try:
            resp = controllers.question_ask(current_user.id, 
                                            question_to=args['question_to'], 
                                            body=args['body'], 
                                            lat=args['coordinate_point'][1], 
                                            lon=args['coordinate_point'][0], 
                                            is_anonymous=args['is_anonymous'], 
                                            )
            
            return resp
        
        except CustomExceptions.BlockedUserException as e:
            abort(404, message="Not found")
        except CustomExceptions.NoPermissionException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")

class QuestionList(restful.Resource):
    @login_required
    def get(self):
        question_list_parser = reqparse.RequestParser()
        question_list_parser.add_argument('since', dest='offset', type=int, default=0, location='args')
        question_list_parser.add_argument('limit', type=int, default=10, location='args')
        args = question_list_parser.parse_args()
        try:
            resp = controllers.question_list(current_user.id, offset=args['offset'], limit=args['limit'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Bad Request")

class QuestionListPublic(restful.Resource):
    @login_required
    def get(self, user_id):
        question_list_parser = reqparse.RequestParser()
        question_list_parser.add_argument('since', dest='offset', type=int, default=0, location='args')
        question_list_parser.add_argument('limit', type=int, default=10, location='args')
        args = question_list_parser.parse_args()
        try:
            resp = controllers.question_list_public(current_user.id, user_id=user_id, offset=args['offset'], limit=args['limit'])
            return resp

        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class QuestionUpvote(restful.Resource):
    @login_required
    def post(self, question_id):
        try:
            resp = controllers.question_upvote(current_user.id, question_id=question_id)
            return resp
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Error")

class QuestionDownvote(restful.Resource):
    @login_required
    def post(self, question_id):
        try:
            resp = controllers.question_downvote(current_user.id, question_id=question_id)
            return resp
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Error")

class QuestionIgnore(restful.Resource):
    @login_required
    def post(self):
        question_ignore_parser = reqparse.RequestParser()
        question_ignore_parser.add_argument('question_id',type=str, required=True, location='json')
        args = question_ignore_parser.parse_args()
        try:
            resp = controllers.question_ignore(current_user.id, question_id=args['question_id'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class PostAdd(restful.Resource):
    @login_required
    def post(self):
        answer_parser = reqparse.RequestParser()
        answer_parser.add_argument('question_id', type=str, required=True, location='form')
        answer_parser.add_argument('video_media', required=True, location='files')
        answer_parser.add_argument('answer_type', type=str, default='video', location='form', choices=['picture', 'video', 'text'])
        answer_parser.add_argument('tags', type=list, default=[], location='form')
        answer_parser.add_argument('lat', type=float, default=0.0, location='form')
        answer_parser.add_argument('lon', type=float, default=0.0, location='form')
        answer_parser.add_argument('client_id', type=str, location='form', default = None)

        args = answer_parser.parse_args()
        
        try:
            resp = controllers.add_video_post(current_user.id, 
                                                question_id=args['question_id'],
                                                video=args['video_media'],
                                                answer_type=args['answer_type'],
                                                lat=args['lat'],
                                                lon=args['lon'],
                                                client_id=args['client_id']
                                                )
            return resp
        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")




class PostLike(restful.Resource):
    @login_required
    def post(self):
        post_like_parser = reqparse.RequestParser()
        post_like_parser.add_argument('post_id', type=str, required=True, location='json')
        args = post_like_parser.parse_args()
        try:
            resp = controllers.post_like(current_user.id, post_id=args['post_id'])
            return resp
        
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class PostUnLike(restful.Resource):
    @login_required
    def post(self):
        post_unlike_parser = reqparse.RequestParser()
        post_unlike_parser.add_argument('post_id', type=str, required=True, location='json')
        args = post_unlike_parser.parse_args()
        try:
            resp = controllers.post_unlike(current_user.id, post_id=args['post_id'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class PostReshare(restful.Resource):
    @login_required
    def post(self):
        post_like_parser = reqparse.RequestParser()
        post_like_parser.add_argument('post_id', type=str, required=True, location='json')
        args = post_like_parser.parse_args()
        try:
            resp = controllers.post_reshare(current_user.id, post_id=args['post_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class PostReshareDelete(restful.Resource):
    @login_required
    def post(self):
        post_like_parser = reqparse.RequestParser()
        post_like_parser.add_argument('post_id', type=str, required=True, location='json')
        args = post_like_parser.parse_args()
        try:
            resp = controllers.post_reshare_delete(current_user.id, post_id=args['post_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")

class PostDelete(restful.Resource):
    @login_required
    def post(self):
        post_delete_parser = reqparse.RequestParser()
        post_delete_parser.add_argument('post_id', type=str, required=True, location='json')
        args = post_delete_parser.parse_args()
        try:
            resp = controllers.post_delete(current_user.id, post_id=args['post_id'])
            return resp
        
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class PostView(restful.Resource):
    def get(self, post_id):
        try:
            client_id =  None
            if len(post_id)<32:
                client_id = post_id

            if current_user.is_authenticated():
                current_user_id = current_user.id
            else:
                current_user_id = None
            
            resp = controllers.post_view(cur_user_id=current_user_id, post_id=post_id, client_id=client_id)
            return resp
        
        except CustomExceptions.BlockedUserException as e:
            abort(404, message="Not found")
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message="Not found")
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class CommentAdd(restful.Resource):
    @login_required
    def post(self):
        comment_add_parser = reqparse.RequestParser()
        comment_add_parser.add_argument('post_id', required=True, type=str, location='json')
        comment_add_parser.add_argument('body', required=True, type=str, location='json')
        comment_add_parser.add_argument('coordinate_point', type=list, default=[None, None], location='json')
        args = comment_add_parser.parse_args()
        try:
            resp = controllers.comment_add(current_user.id,
                                            post_id=args['post_id'],
                                            body=args['body'],
                                            lat=args['coordinate_point'][1],
                                            lon=args['coordinate_point'][0])
            return resp
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class CommentDelete(restful.Resource):
    @login_required
    def post(self):
        comment_delete_parser = reqparse.RequestParser()
        comment_delete_parser.add_argument('comment_id', required=True, type=str, location='json')
        args = comment_delete_parser.parse_args()
        try:
            resp = controllers.comment_delete(current_user.id, comment_id=args['comment_id'])
            return resp

        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")

class CommentList(restful.Resource):
    @login_required
    def get(self):
        comment_list_parser = reqparse.RequestParser()
        comment_list_parser.add_argument('post_id', type=str, required=True, location='args')
        comment_list_parser.add_argument('since', dest='offset', default=0, type=int, location='args')
        comment_list_parser.add_argument('limit', type=int, location='args', default=10)
        args = comment_list_parser.parse_args()
        try:
            resp = controllers.comment_list(current_user.id,
                                            post_id=args['post_id'],
                                            offset=args['offset'],
                                            limit=args['limit'])
            return resp
        
        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class TimelineUser(restful.Resource):
    def get(self, user_id):
        user_timeline_parser = reqparse.RequestParser()
        user_timeline_parser.add_argument('offset', type=int, default=0, location='args')
        user_timeline_parser.add_argument('limit', type=int, default=10, location='args')
        args = user_timeline_parser.parse_args()
        try:
            if current_user.is_authenticated():
                if user_id =='me':
                    user_id = current_user.id
                cur_user_id = current_user.id
            else:
                if user_id =='me':
                    raise CustomExceptions.NoPermissionException()
                cur_user_id = None
            
            resp = controllers.get_user_timeline(cur_user_id, 
                                                user_id=user_id,
                                                offset=args['offset'],
                                                limit=args['limit'])
            return resp
        except CustomExceptions.UserNotFoundException, e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class TimelineHome(restful.Resource):
    @login_required
    def get(self):
        timeline_parser = reqparse.RequestParser()
        timeline_parser.add_argument('offset', type=int, default=0, location='args')
        timeline_parser.add_argument('limit', type=int, default=10, location='args')
        timeline_parser.add_argument('X-Deviceid', type=str, required=True, location='headers')
        timeline_parser.add_argument('web', type=str, default=False, location='args')
        args = timeline_parser.parse_args()
        
        if 'web' in args['X-Deviceid']:
            args['web'] = True
        try:
            resp = controllers.home_feed(current_user.id,
                                        offset=args['offset'],
                                        limit=args['limit'],
                                        web=args['web'])
            return resp

        except CustomExceptions.UserNotFoundException, e:
            abort(403, message='Unauthorised')

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")



class DiscoverPost(restful.Resource):
    def get(self):
        discover_post_parser = reqparse.RequestParser()
        discover_post_parser.add_argument('offset', type=int, default=0, location='args')
        discover_post_parser.add_argument('limit', type=int, default=10, location='args')
        discover_post_parser.add_argument('lat', type=float, location='args')
        discover_post_parser.add_argument('lon', type=float, location='args')
        discover_post_parser.add_argument('X-Deviceid', type=str, required=True, location='headers')
        discover_post_parser.add_argument('web', type=int, default=False, location='args')
        discover_post_parser.add_argument('visit', type=int, default=0, location='args')


        args = discover_post_parser.parse_args()

        if 'web' in args['X-Deviceid']:
            args['web'] = True
        
        try:
            if current_user.is_authenticated():
                current_user_id = current_user.id
                
            else:
                current_user_id = None
            
            resp = controllers.discover_post_in_cqm(cur_user_id=current_user_id,
                                                offset=args['offset'],
                                                limit=args['limit'],
                                                web = args['web'])
          # resp = controllers.discover_posts(cur_user_id=current_user_id,
          #                                     lat=args.get('lat'),
          #                                     lon=args.get('lon'),
          #                                     offset=args['offset'],
          #                                     limit=args['limit'], 
          #                                     web=args['web'],
          #                                     visit=args['visit'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


reset_password_parser = reqparse.RequestParser()
reset_password_parser.add_argument('password', type=str, required = True, location='json')

class ForgotPassword(restful.Resource):
    def post(self):
        forgot_password_parser = reqparse.RequestParser()
        forgot_password_parser.add_argument('username', type=str, required=True, location='json')
        args = forgot_password_parser.parse_args()
        print args
        try:
            username = args['username']
            email = None
            if '@' in username and '.' in username:
                email = username
                username = None
            return controllers.create_forgot_password_token(username, email)
        
        except CustomExceptions.UserNotFoundException:
            abort(404, message='User not Found')
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")

class CheckForgotPasswordToken(restful.Resource):
    def post(self):
        check_forgot_password_token_password = reqparse.RequestParser()
        check_forgot_password_token_password.add_argument('token', type=str, required = True, location='json')
        args = check_forgot_password_token_password.parse_args()
        try:
            return controllers.check_forgot_password_token(args['token'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")

class ResetPassword(restful.Resource):
    def post(self, token):
        args = reset_password_parser.parse_args()
        try:
            resp = controllers.reset_password(token, args['password'])
            return resp
        except CustomExceptions.ObjectNotFoundException as e:
            abort(403, message = '{"success":false, "error":"invalidToken", "message":"The token you provided is not valid anymore"}')
        except CustomExceptions.PasswordTooShortException as e:
            abort(400, message = '{"success":false, "error":"shortPassword", "message":"The password should be minimum 6 characters"}')
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Failed")


class InstallRef(restful.Resource):
    def post(self):
        install_ref_parser = reqparse.RequestParser()
        install_ref_parser.add_argument('device_id', type=str, location='json', required=True)
        install_ref_parser.add_argument('url', type=str, location='json', required=True)
        args = install_ref_parser.parse_args()
        try:
            controllers.install_ref(args['device_id'], args['url'])
            return {'success':True}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')

class BadUsernames(restful.Resource):
    def get(self):
        badusername_parser = reqparse.RequestParser()
        badusername_parser.add_argument('timestamp', type=int, location='args', default=0)
        args = badusername_parser.parse_args()
        try:
            if args['timestamp'] < config.UNAVAILABLE_USERNAMES_LAST_UPDATED:
                return {'ulist':config.UNAVAILABLE_USERNAMES, 'changed':True}
            return {'ulist':[], 'changed':False}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Error')



class Notifications(restful.Resource):
    @login_required
    def get(self):
        get_notifications_parser = reqparse.RequestParser()
        get_notifications_parser.add_argument('offset', type=int, default=0, location='args')
        get_notifications_parser.add_argument('limit', type=int, default=10, location='args')
        get_notifications_parser.add_argument('type', type=str, default='me', location='args')
        args = get_notifications_parser.parse_args()
        try:
            resp = controllers.get_notifications(current_user.id,
                                                    notification_category=args['type'],
                                                    offset = args['offset'],
                                                    limit = args['limit'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Internal Server Error')


class NotificationCount(restful.Resource):
    @login_required
    def get(self):
        try:
            count = controllers.get_notification_count(current_user.id)
            return {'count': count}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='Internal Server Error')

class Logout(restful.Resource):
    @login_required
    def post(self):
        logout_parser = reqparse.RequestParser()
        logout_parser.add_argument('X-Deviceid', dest='device_id', type=str, required=True, location='headers')
        logout_parser.add_argument('X-Token', dest='access_token', type=str, required=True, location='headers')
        args = logout_parser.parse_args()
        
        try:
            success = controllers.logout(access_token=args['access_token'], device_id=args['device_id'])
            return {'success': success}

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            return {'success': False}


class QuestionImageCreator(restful.Resource):
    def get(self, question_id):
        try:
            from flask import send_file
            question_image = controllers.get_question_authors_image(question_id)

            return send_file(question_image, as_attachment=True, attachment_filename='%s.jpg'%(question_id))
        
        except CustomExceptions.ObjectNotFoundException:
            abort(404, message='Image not Found')

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=str(traceback.format_exc(e)))

class InterviewVideoResource(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('offset', type=int, location = 'args', default = 0)
        parser.add_argument('limit', type=int, location = 'args', default = 10)
        args = parser.parse_args()
        try:
            return controllers.interview_media_controller(args['offset'], args['limit'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=str(traceback.format_exc(e)))        

class WebHiringForm(restful.Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='form', required=True)
        parser.add_argument('email', type=str, location='form', required=True)
        parser.add_argument('phone', type=str, location='form', default=None)
        parser.add_argument('role', type=str, location='form', default=None)

        args = parser.parse_args()
        try:
            return controllers.web_hiring_form(args['name'], args['email'], args['phone'], args['role'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=str(traceback.format_exc(e)))


class VideoView(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str, location='args', required=True)
        args = parser.parse_args()
        try:
            from flask import redirect
            controllers.view_video(args['url'])
            return redirect(args['url'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            return redirect(args['url'])


class Search(restful.Resource):
    def get(self):
        from flask import request
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, location='args', required = True)
        parser.add_argument('offset', type=int, location='args', default = 0)
        parser.add_argument('limit', type=int, location='args', default = 10)
        args = parser.parse_args()
        try:
            version_code = request.headers.get('X-Version-Code', None)
            if current_user.is_authenticated():
                current_user_id = current_user.id
            else:
                current_user_id = None
            
            return controllers.search(cur_user_id=current_user_id,
                                        query=args['q'],
                                        offset=args['offset'],
                                        limit=args['limit'],
                                        version_code = version_code)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)

class ContactUs(restful.Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location ='json', required = True )
        parser.add_argument('email', type=str, location ='json', required = True )
        parser.add_argument('organisation', type=str, location ='json', required = True )
        parser.add_argument('message', type=str, location ='json', required = True )
        parser.add_argument('phone', type=str, location ='json', default = '000-000-0000')
        args = parser.parse_args()
        try:
            return controllers.add_contact(args['name'], args['email'], args['organisation'], args['message'], args['phone'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=str(traceback.format_exc(e)))


class SearchDefault(restful.Resource):
    def get(self):
        return controllers.search_default()
