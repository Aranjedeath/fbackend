import sys
import traceback
import flask
from flask import request
from flask.ext import restful
from flask.ext.restful import abort
from flask.ext.restful import reqparse
from flask.ext.login import login_required, current_user
from raygun4py import raygunprovider

import controllers
import CustomExceptions
import json
from configs import config

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)

ALLOWED_PICTURE_FORMATS = ['jpg', 'jpeg']
ALLOWED_VIDEO_FORMATS = ['mp4']

device_id_argument_help = "device_id should be str(16) for android, str(32) for iOS, 'web' for browsers"
push_id_argument_help = "push_id will be GCM id for Android and APN id for iOS"
internal_server_error_message = "Something went wrong. Please try again in a few seconds"


class RegisterEmail(restful.Resource):

    #==POST==#
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('email'        , type=str, required=True, location='json')
    post_parser.add_argument('device_id'    , type=str, required=True, location='json', help=device_id_argument_help)
    post_parser.add_argument('full_name'    , type=str, required=True, location='json')
    post_parser.add_argument('password'     , type=str, default=None, location='json')
    post_parser.add_argument('username'     , type=str, required=False, location='json', default = None, help="username should be 6 to 24 characters and can only contain A-Z, a-z, 0-9 and _ ")
    
    post_parser.add_argument('gender'       , type=str, default='M', location='json', choices=['M', 'F'])
    post_parser.add_argument('user_type'    , type=int, location='json', default = 0)
    
    post_parser.add_argument('lat'          , type=str, default=None, location='json')
    post_parser.add_argument('lon'          , type=str, default=None, location='json')
    post_parser.add_argument('location_name', type=str, default=None, location='json')
    post_parser.add_argument('country_name' , type=str, default=None, location='json')
    post_parser.add_argument('country_code' , type=str, default=None, location='json')
    
    post_parser.add_argument('phone_num'    , type=str, location='json')
    post_parser.add_argument('push_id'      , type=str, location='json', help=push_id_argument_help)

    def post(self):
        """
        Register a new user with email and password.

        Controller Functions Used:
            -register_email_user

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.register_email_user( email         = args['email'],
                                                    password      = args['password'],
                                                    full_name     = args['full_name'],
                                                    device_id     = args.get('device_id'),
                                                    push_id       = args.get('push_id'),
                                                    phone_num     = args.get('phone_num'),
                                                    username      = args.get('username'),
                                                    gender        = args.get('gender'),
                                                    user_type     = args['user_type'],
                                                    user_title    = args.get('user_title'),
                                                    lat           = args['lat'],
                                                    lon           = args['lon'],
                                                    location_name = args['location_name'],
                                                    country_name  = args['country_name'],
                                                    country_code  = args['country_code']
                                                )
        except CustomExceptions.UserAlreadyExistsException as e:
            abort(409, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class LoginSocial(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('device_id'            , type=str, required=True, location='json', help=device_id_argument_help)
    post_parser.add_argument('external_access_token', type=str, location='json', required=True)
    post_parser.add_argument('external_token_secret', type=str, location='json', help="external_token_secret is only required for services with access_token and access_secret auth, e.g. Twitter")
    post_parser.add_argument('social_user_id'       , type=str, location='json', required=True)
    post_parser.add_argument('push_id'              , type=str, location='json', help=push_id_argument_help)
    post_parser.add_argument('user_type'            , type=int, location='json', default=0, choices=[0, 2], help="user_type 0 for normal users, 2 for celebrities.")
    post_parser.add_argument('user_title'           , type=str, location='json', default=None, help="user_title is used only when user_type is 2.")
    
    def post(self, login_type):
        """
        Login/Register user with 3rd Party Login.
        
        If user exists, they will be logged in. Else new user profile will be created.

        Support for:
            - Facebook(login_type = '/facebook')
            - Twitter(login_type  = '/twitter')
            - Google(login_type   = '/google')


        Controller Functions Used:
            - login_user_social

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            if login_type not in ['google', 'facebook', 'twitter']:
                abort(404, message='Not Found')
            if login_type == 'twitter' and not args.get('external_token_secret'):
                abort(400, message='external_token_secret is a required Field')
            
            return controllers.login_user_social(social_type          =login_type,
                                                 social_id            =args['social_user_id'],
                                                 external_access_token=args['external_access_token'],
                                                 device_id            =args['device_id'],
                                                 push_id              =args.get('push_id'),
                                                 external_token_secret=args.get('external_token_secret'),
                                                 user_type            =args.get('user_type'),
                                                 user_title           =args.get('user_title')
                                                 )
        
        except CustomExceptions.InvalidTokenException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class LoginEmail(restful.Resource):
    
    def get(self):
        """
        Used internally by the api. Users trying to access endpoints without valid authentication
            will be redirected to this. It always returns a 403 status_code.
        """
        abort(403, message='Your Accesstoken has expired, Please login again')


    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username' , type=str, required=True, location='json', help='username argument should contain either username or email.')
    post_parser.add_argument('password' , type=str, required=True, location='json')
    post_parser.add_argument('device_id', type=str, required=True, location='json', help=device_id_argument_help)
    post_parser.add_argument('push_id'  , type=str, location='json', default=None, help=push_id_argument_help)
    
    def post(self):
        """
        Login user with email/username and password.

        Controller Functions Used:
            - login_email_new

        Authentication: None
        """

        args = self.post_parser.parse_args()
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
            abort(500, message=internal_server_error_message)



class UserProfile(restful.Resource):

    def get(self, user_id):
        """
        Returns profile information of the user.

        user_id can be username or user_id of the user or 'me'(only with valid authentication).

        Controller Functions Used:
            - user_view_profile

        Authentication: Optional
        """
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
                    raise CustomExceptions.UserNotFoundException()
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
            abort(500, message=internal_server_error_message)


class UserUpdateForm(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('first_name'     , type=str, location='form')
    post_parser.add_argument('bio'            , type=str, location='form', help="bio should be str(200)")
    post_parser.add_argument('user_title'     , type=str, location='form')
    post_parser.add_argument('profile_picture', type=file, location='files', help="profile_picture should be an jpg/jpeg file")
    post_parser.add_argument('profile_video'  , type=file, location='files', help="profile_video should be a .mp4 file")
    
    @login_required
    def post(self, user_id):
        """
        Updates profile information of the user.
        If value of an optional argument is None or is not provided, they will retain their old value.

        user_id should be 'me'

        Controller Functions Used:
            - user_update_profile_form

        Authentication: Required
        """
        from flask import request
        #print '****', request.form, request.files
        args = self.post_parser.parse_args()
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
            abort(500, message=internal_server_error_message)


class UserProfileRequest(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('request_by', type=str, default='', location = 'json')
    post_parser.add_argument('request_type', type=str, required=True, location = 'json', choices=config.REQUEST_TYPE)

    @login_required
    def post(self):
        """
        Requests the user for a profile update

        Controller Functions Used:
            - user_profile_request

        Authentication: Required
        """
        args = self.post_parser.parse_args()

        try:
            resp = controllers.user_profile_request(current_user_id=current_user.id, request_by=args['request_by'],
                                                    request_type=args['request_type'])
            return resp

        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class SlugItem(restful.Resource):

    def get(self, username, slug):
        """
        Returns question if question for slug is not answered, returns post instead.

        username: is username of the question_to/answer_author
                    user will be redirected to the right url if the username is wrong.
        slug: is the question slug

        Controller Functions Used:
            - get_item_from_slug

        Authentication: Optional
        """

        from app import api

        current_user_id = None
        if current_user.is_authenticated():
            current_user_id = current_user.id        
        try:
            resp = controllers.get_item_from_slug(current_user_id, username, slug)
            if resp['redirect']:
                return {'redirect':True, 'location':api.url_for(SlugItem, username=resp['username'], slug=slug), 'code':301}
            return resp

        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class UserFollow(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('user_id', required=True, type=str, location='json', help="user_id must be user_id of the user to be followed")

    @login_required
    def post(self):
        """
        Lets current user follow the user with user_id provided in argument.

        Controller Functions Used:
            - user_follow

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
        try:
            resp = controllers.user_follow(current_user.id, user_id=args['user_id'])
            return resp

        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserUnfollow(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('user_id', required=True, type=str, location='json', help="user_id must be user_id of the user to be followed")

    @login_required
    def post(self):
        """
        Lets current user unfollow the user with user_id provided in argument.

        Controller Functions Used:
            - user_unfollow

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.user_unfollow(current_user.id, user_id=args['user_id'])
            return resp

        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserFollowers(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', default=0, type=int, location='args', help="offset must be integer >=0")
    get_parser.add_argument('limit' , default=10, type=int, location='args', help="limit must be >=0")
    
    def get(self, user_id):
        """
        Returns list of followers of a user.
        user_id can be username or user_id of the user or 'me'(only with valid authentication).

        Controller Functions Used:
            - user_followers

        Authentication: Optional
        """
        
        username=None

        if current_user.is_authenticated():
            current_user_id = current_user.id
        else:
            current_user_id = None

        if user_id == 'me':
            user_id = current_user_id
        elif len(user_id) < 32:
            username = user_id

        args = self.get_parser.parse_args()
        
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
            abort(500, message=internal_server_error_message)


class UserBlock(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('user_id', required=True, type=str, location='json', help="user_id must be user_id of the user to be blocked")

    @login_required
    def post(self):
        """
        Lets current user block the user with user_id provided in argument.

        Controller Functions Used:
            - user_block

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
        try:
            resp = controllers.user_block(current_user.id, user_id=args['user_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserUnblock(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('user_id', required=True, type=str, location='json', help="user_id must be user_id of the user to be unblocked")
    
    @login_required
    def post(self):
        """
        Lets current user unblock the user with user_id provided in argument.

        Controller Functions Used:
            - user_unblock

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
        try:
            resp = controllers.user_unblock(current_user.id, user_id=args['user_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserBlockList(restful.Resource):

    @login_required
    def get(self):
        """
        Returns list of users the current user has blocked.

        Controller Functions Used:
            - user_block_list

        Authentication: Required
        """
        try:
            resp = controllers.user_block_list(current_user.id)
            return resp
        
        except CustomExceptions.BadRequestException as e:
            print traceback.format_exc(e)
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class ChangeUsername(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username', required=True, type=str, location='json', help="username should be the new username.")
    post_parser.add_argument('id'      , type=str, location='json', help="id is required only for admin purposes. id of the user whose username is to be changed.")

    @login_required
    def post(self):
        """
        Changes username of the current_user.
        For admin users, changes username of the user with user_id=id if id is provided

        Controller Functions Used:
            - user_change_username

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
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
            abort(500, message=internal_server_error_message)


class ChangePassword(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('password', required=True, type=str, location='json', help="password must be the changed password")

    @login_required
    def post(self):
        """
        Changes password of the current_user.

        Controller Functions Used:
            - user_change_password

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.user_change_password(current_user.id, new_password=args['password'])
            return resp

        except CustomExceptions.UnameUnavailableException, e:
            abort(400, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserExists(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username'    , type=str, location='json', default=None)
    post_parser.add_argument('email'       , type=str, location='json', default=None)
    post_parser.add_argument('phone_number', type=str, location='json', default=None)

    def post(self):
        """
        Helps to check if a user with given username or email exists.

        Controller Functions Used:
            - user_exists

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.user_exists(username=args['username'], email=args['email'], phone_number=args['phone_number'])
            return resp
        except CustomExceptions.BadRequestException as e:
            print traceback.format_exc(e)
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class UserSettings(restful.Resource):
    
    @login_required
    def get(self):
        """
        Returns settings of the current_user.

        Controller Functions Used:
            - user_get_settings

        Authentication: Required
        """
        try:
            resp = controllers.user_get_settings(current_user.id)
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


    post_parser = reqparse.RequestParser()
    post_parser.add_argument('allow_anonymous_question', type=bool, location='json', required=True)
    post_parser.add_argument('notify_like'             , type=bool, location='json', required=True)
    post_parser.add_argument('notify_follow'           , type=bool, location='json', required=True)
    post_parser.add_argument('notify_question'         , type=bool, location='json', required=True)
    post_parser.add_argument('notify_comments'         , type=bool, location='json', required=True)
    post_parser.add_argument('notify_mention'          , type=bool, location='json', required=True)
    post_parser.add_argument('notify_answer'           , type=bool, location='json', required=True)
    post_parser.add_argument('timezone'                , type=int, location='json', default=0, help="timezone should be the offset of user's timezone from UTC in seconds")

    @login_required
    def post(self):
        """
        Updates settings of the current_user.

        Controller Functions Used:
            - user_update_settings

        Authentication: Required
        """
        
        args = self.post_parser.parse_args()
        
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
            abort(500, message=internal_server_error_message)


class UserLocation(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('coordinate_point', required=True, location='json', type=list, help='coordinate_point should be of format [longitude, latitude] where both of them are float.')
    post_parser.add_argument('country'         , location='json', type=str, default=None)
    post_parser.add_argument('country_code'    , location='json', type=str, default=None, help='country_code should be two letter country code.')
    post_parser.add_argument('loc_name'        , location='json', type=str, default=None)

    def post(self):
        """
        Updates location of the current_user.

        Controller Functions Used:
            - user_update_location

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
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
            abort(500, message=internal_server_error_message)


class UpdatePushId(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('X-Deviceid', type=str, required=True, location = 'headers', dest='device_id', help="device_id will be the device_id of the user whose push_id is to be updated.")
    post_parser.add_argument('push_id'   , type=str, location='json', required=True, help=push_id_argument_help)
    
    @login_required
    def post(self):
        """
        Updates push_id of the current_user.

        Controller Functions Used:
            - update_push_id

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            controllers.update_push_id(current_user.id, device_id=args['device_id'], push_id=args['push_id'])
            return {'success' : True}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class UserUpdateToken(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('acc_type', type=str, location='json', default='facebook', choices=['facebook'])
    post_parser.add_argument('token'   , type=str, location='json', required=True)
    
    @login_required
    def post(self):
        """
        Updates 3rd party auth token of the current_user, e.g. Facebook auth token.

        Controller Functions Used:
            - user_update_access_token

        Authentication: Required
        """
        args = self.post_parser.parse_args()
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
            abort(500, message=internal_server_error_message)


class QuestionAsk(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('question_to'     , type=str, required=True, location='json', help="question_to must be user_id of the user to whom the question is being asked.")
    post_parser.add_argument('body'            , type=str, required=True, location='json')
    post_parser.add_argument('coordinate_point', type=list, default=[None, None], location='json')
    post_parser.add_argument('is_anonymous'    , type=bool, required=True, location='json')

    @login_required
    def post(self):
        """
        Lets the current_user ask question to a given user.

        Controller Functions Used:
            - question_ask

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
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
            abort(404, message=str(e))
        except CustomExceptions.NoPermissionException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class QuestionView(restful.Resource):
    
    def get(self, question_id):
        """
        Returns a single question.
        question_id can be id of the post or short_id of the post.

        Controller Functions Used:
            - question_view

        Authentication: Optional
        """
        try:
            short_id =  None
            if len(question_id)<32:
                short_id = question_id

            if current_user.is_authenticated():
                current_user_id = current_user.id
            else:
                current_user_id = None
            
            resp = controllers.question_view(current_user_id=current_user_id, question_id=question_id, short_id=short_id)
            return resp
        
        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class QuestionList(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('since', dest='offset', type=int, default=0, location='args')
    get_parser.add_argument('limit', type=int, default=10, location='args')
    get_parser.add_argument('X-Version-Code', type=float, location='headers', default=0)



    @login_required
    def get(self):
        """
        Returns list of questions asked to the current_user.

        Controller Functions Used:
            - question_list

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            resp = controllers.question_list(current_user.id,
                                                offset=args['offset'],
                                                limit=args['limit'],
                                                version_code=args['X-Version-Code']
                                                )
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class QuestionListPublic(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('since', dest='offset', type=int, default=0, location='args')
    get_parser.add_argument('limit', type=int, default=10, location='args')
    get_parser.add_argument('X-Version-Code', type=float, location='headers', default=None)

    
    def get(self, user_id):
        """
        Returns list of public questions asked to the user with user_id.
            user_id can be the id or username of the user whose question list id to be fetched.

        Controller Functions Used:
            - question_list_public

        Authentication: Optional
        """
        args = self.get_parser.parse_args()
        try:
            current_user_id = None
            if current_user.is_authenticated():
                current_user_id = current_user.id
            
            username = None
            if len(user_id)<32:
                username = user_id
            resp = controllers.question_list_public(current_user_id, user_id=user_id,
                                                    username=username, offset=args['offset'],
                                                    limit=args['limit'], version_code=args['X-Version-Code'])
            return resp

        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))

        except CustomExceptions.UserNotFoundException as e:
            abort(404, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class QuestionUpvote(restful.Resource):
    @login_required
    def post(self, question_id):
        """
        Lets the current_user upvote a question.

        Controller Functions Used:
            - question_upvote

        Authentication: Required
        """
        try:
            resp = controllers.question_upvote(current_user.id, question_id=question_id)
            return resp
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class QuestionDownvote(restful.Resource):
    @login_required
    def post(self, question_id):
        """
        Lets the current_user downvote a question.

        Controller Functions Used:
            - question_downvote

        Authentication: Required
        """
        try:
            resp = controllers.question_downvote(current_user.id, question_id=question_id)
            return resp
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class QuestionIgnore(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('question_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user ignore a question asked to the current_user.

        Controller Functions Used:
            - question_ignore

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.question_ignore(current_user.id, question_id=args['question_id'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class PostAdd(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('question_id', type=str, required=True, location='form', help="question_id should be the id of the question to be answered")
    post_parser.add_argument('video_media', required=True, type=file, location='files', help="video_media should be a .mp4 file")
    post_parser.add_argument('answer_type', type=str, default='video', location='form', choices=['picture', 'video', 'text'])
    post_parser.add_argument('tags'       , type=list, default=[], location='form')
    post_parser.add_argument('lat'        , type=float, default=0.0, location='form')
    post_parser.add_argument('lon'        , type=float, default=0.0, location='form')
    post_parser.add_argument('client_id'  , type=str, location='form', default = None, help="client_id is the short id of the answer to be post. Ideally it should be generated and sent by the client")
    
    @login_required
    def post(self):
        """
        Lets the current_user answer a question.

        Controller Functions Used:
            - add_video_post

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        print args  
        
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
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)




class PostLike(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user like an answer.

        Controller Functions Used:
            - post_like

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.post_like(current_user.id, post_id=args['post_id'])
            return resp
        
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class PostUnLike(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user unlike an answer.

        Controller Functions Used:
            - post_unlike

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.post_unlike(current_user.id, post_id=args['post_id'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)




class PostShared(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    post_parser.add_argument('platform', type=str, required=True, location='json', choices=['whatsapp', 'facebook', 'hike', 'twitter', 'other'], help='platform is the lowercase name of the plaform the post is being shared on.')
    
    @login_required
    def post(self):
        """
        Updates the count of shares for a post on a given platform

        Controller Functions Used:
            - update_post_share

        Authentication: Required
        """
    
        args = self.post_parser.parse_args()
        try:
            resp = controllers.update_post_share(current_user.id, post_id=args['post_id'], platform=args['platform'].lower())
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class PostReshare(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user reshare an answer. Reshared answers appear on users profile timeline.

        Controller Functions Used:
            - post_reshare

        Authentication: Required
        """
    
        args = self.post_parser.parse_args()
        try:
            resp = controllers.post_reshare(current_user.id, post_id=args['post_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class PostReshareDelete(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user deleted reshare of an answer. Reshared answers appear on users profile timeline.
            Once reshare is deleted, it will be removed from timeline

        Controller Functions Used:
            - post_reshare_delete

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.post_reshare_delete(current_user.id, post_id=args['post_id'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class PostDelete(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id', type=str, required=True, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user delete their answer.

        Controller Functions Used:
            - post_delete

        Authentication: Required
        """
        
        args = self.post_parser.parse_args()
        try:
            resp = controllers.post_delete(current_user.id, post_id=args['post_id'])
            return resp
        
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class PostView(restful.Resource):
    
    def get(self, post_id):
        """
        Returns a single post.
        post_id can be id of the post or client_id of the post.

        Controller Functions Used:
            - post_view

        Authentication: Optional
        """
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
            abort(404, message=e)
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=e)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class CommentAdd(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('post_id'         , required=True, type=str, location='json')
    post_parser.add_argument('body'            , required=True, type=str, location='json')
    post_parser.add_argument('coordinate_point', type=list, default=[None, None], location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user add comment to a post.

        Controller Functions Used:
            - comment_add

        Authentication: Required
        """
        
        args = self.post_parser.parse_args()
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
            abort(500, message=internal_server_error_message)


class CommentDelete(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('comment_id', required=True, type=str, location='json')
    
    @login_required
    def post(self):
        """
        Lets the current_user delete a comment. Either the current user should be comment_author or answer_author of the post.

        Controller Functions Used:
            - comment_delete

        Authentication: Required
        """
        
        args = self.post_parser.parse_args()
        try:
            resp = controllers.comment_delete(current_user.id, comment_id=args['comment_id'])
            return resp

        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class CommentList(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('post_id', type=str, required=True, location='args')
    get_parser.add_argument('since'  , dest='offset', default=0, type=int, location='args')
    get_parser.add_argument('limit'  , type=int, location='args', default=10)
    
    def get(self):
        """
        Returns a list of comment on a post.

        Controller Functions Used:
            - comment_list

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            if current_user.is_authenticated():
                user_id = current_user.id
                comments = controllers.comment_list(current_user.id,
                                                    post_id=args['post_id'],
                                                    offset=args['offset'],
                                                    limit=args['limit'])
            else:
                comments = controllers.comment_list(None,
                                                    post_id=args['post_id'],
                                                    offset=args['offset'],
                                                    limit=args['limit'])
            return comments
        
        except CustomExceptions.BlockedUserException as e:
            abort(404, message=str(e))
        except CustomExceptions.PostNotFoundException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class TimelineUser(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', type=int, default=0, location='args')
    get_parser.add_argument('limit' , type=int, default=10, location='args')
    
    def get(self, user_id):
        """
        Returns the profile timeline of the user.
        user_id should be id of the user or 'me' for current_user's timeline.

        Controller Functions Used:
            - get_user_timeline

        Authentication: Optional
        """
        
        args = self.get_parser.parse_args()
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
            abort(500, message=internal_server_error_message)


class TimelineHome(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset'    , type=int, default=0, location='args')
    get_parser.add_argument('limit'     , type=int, default=10, location='args')
    get_parser.add_argument('X-Deviceid', type=str, required=True, location='headers')
    
    @login_required
    def get(self):
        """
        Returns the home feed of the current_user.

        Controller Functions Used:
            - home_feed

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        
        if 'web' in args['X-Deviceid']:
            args['web'] = True
        try:
            resp = controllers.home_feed(current_user.id,
                                        offset=args['offset'],
                                        limit=args['limit'],
                                        web=args.get('web'))
            return resp

        except CustomExceptions.UserNotFoundException, e:
            abort(403, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class DiscoverPost(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset'        , type=int, default=0, location='args')
    get_parser.add_argument('limit'         , type=int, default=10, location='args')
    get_parser.add_argument('lat'           , type=float, location='args')
    get_parser.add_argument('lon'           , type=float, location='args')
    get_parser.add_argument('X-Deviceid'    , type=str, required=True, location='headers')
    get_parser.add_argument('visit'         , type=int, default=0, location='args', help="visit should be the time difference of the current time and user's first visit in seconds for unauthorised requests")
    get_parser.add_argument('append_top'    , type=str, default='', location='args', help="append_top should be username or comma separayed username. These users will be appended on top of the feed. Only valid when offset=0")
    get_parser.add_argument('X-Deviceid'    , type=str, dest='device_id', required=True, location='headers', help=device_id_argument_help)
    get_parser.add_argument('X-Version-Code', type=float, dest='version_code', default=0, location='headers', help="version_code of the app.")

    def get(self):
        """
        Returns the discover feed.

        Controller Functions Used:
            - discover_post_in_cqm

        Authentication: Optional
        """
    
        args = self.get_parser.parse_args()

        if 'web' in args['X-Deviceid']:
            args['web'] = True
        
        try:
            if current_user.is_authenticated():
                current_user_id = current_user.id
                
            else:
                current_user_id = None

            resp = controllers.get_new_discover(current_user_id=current_user_id,
                                    offset=args['offset'],
                                    limit=args['limit'],
                                    device_id=args['device_id'],
                                    version_code=args['version_code'],
                                    visit=args['visit'],
                                    append_top=args['append_top'])
            return resp

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class ForgotPassword(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('username', type=str, required=True, location='json', help="username should be either username or email of the user")
    
    def post(self):
        """
        Sends a password reset mail to the user whose username or email is provided.

        Controller Functions Used:
            - create_forgot_password_token

        Authentication: None
        """

        args = self.post_parser.parse_args()
        print args
        try:
            username = args['username']
            email = None
            if '@' in username and '.' in username:
                email = username
                username = None
            return controllers.create_forgot_password_token(username, email)
        
        except CustomExceptions.UserNotFoundException as e:
            abort(404, message=str(e))
        except CustomExceptions.BadRequestException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class CheckForgotPasswordToken(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('token', type=str, required = True, location='json')
    
    def post(self):
        """
        Used to check validity of a reset password token.

        Controller Functions Used:
            - check_forgot_password_token

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.check_forgot_password_token(args['token'])
        except CustomExceptions.BadRequestException as e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class ResetPassword(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('password', type=str, required = True, location='json')

    def post(self, token):
        """
        Resets password of the user from the reset password token.
        token should be a valid.

        Controller Functions Used:
            - reset_password

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            resp = controllers.reset_password(token, args['password'])
            return resp
        except CustomExceptions.ObjectNotFoundException as e:
            abort(403, message=str(e))
        except CustomExceptions.PasswordTooShortException as e:
            abort(400, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class Notifications(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', type=int, default=0, location='args')
    get_parser.add_argument('limit' , type=int, default=10, location='args')
    get_parser.add_argument('type'  , type=str, default='me', location='args', choices=['me', 'news'])
    get_parser.add_argument('X-deviceid', type=str, required=True, location='headers')
    get_parser.add_argument('X-Version-Code', type=float, default=0, location='headers')

    
    @login_required
    def get(self):
        """
        Returns list of notifications for the current_user

        Controller Functions Used:
            - get_notifications

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            resp = controllers.get_notifications(cur_user_id=current_user.id,
                                                device_id=args['X-deviceid'],
                                                version_code=args['X-Version-Code'],
                                                notification_category=args['type'],
                                                offset=args['offset'],
                                                limit=args['limit'])
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class NotificationCount(restful.Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('X-deviceid', type=str, required=True, location='headers')
    get_parser.add_argument('X-Version-Code', type=float, default=0, location='headers')

    
    @login_required
    def get(self):
        """
        Returns count of unread notifications for the current_user

        Controller Functions Used:
            - get_notification_count

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            count = controllers.get_notification_count(current_user.id, device_id=args['X-deviceid'], version_code=args['X-Version-Code'])
            return {'count': count}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class PushNotificationSeen(restful.Resource):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('push_notification_id', type=str, default='',location = 'json')


    @login_required
    def post(self):
        """
        Used to mark a push notification as 'seen' by the
        user on their device

        """
        args = self.post_parser.parse_args()

        try:
            controllers.push_notification_seen(push_notification_id=args['push_notification_id'])

            return {'success': True}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class QuestionCount(restful.Resource):
    
    @login_required
    def get(self):
        """
        Returns count of pending questions for the logged in user

        Controller Functions Used:
            - question_count

        Authentication: Required
        """
        try:
            resp = controllers.question_count(current_user.id)
            return resp
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class Search(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('q'             , type=str, location='args', required = True, help="q should be the query string")
    get_parser.add_argument('offset'        , type=int, location='args', default = 0)
    get_parser.add_argument('limit'         , type=int, location='args', default = 10)
    get_parser.add_argument('X-Version-Code', type=float, location='headers', default=None)
    
    def get(self):
        """
        Returns search results for the query string provided in the arguments
        
        Controller Functions Used:
            - get_parser

        Authentication: Optional
        """
        args = self.get_parser.parse_args()
        try:
            if current_user.is_authenticated():
                current_user_id = current_user.id
            else:
                current_user_id = None
            
            return controllers.query_search(cur_user_id=current_user_id,
                                        query=args['q'],
                                        offset=args['offset'],
                                        limit=args['limit'],
                                        version_code = args['X-Version-Code'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class SearchDefault(restful.Resource):
    
    def get(self):
        """
        Returns the results for the default search page.
        
        Controller Functions Used:
            - search_default

        Authentication: Optional
        """
        try:
            current_user_id = None
            if current_user.is_authenticated():
                current_user_id = current_user.id

            return controllers.search_default(cur_user_id=current_user_id)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class Logout(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('X-Deviceid', dest='device_id', type=str, required=True, location='headers', help=device_id_argument_help)
    post_parser.add_argument('X-Token'   , dest='access_token', type=str, required=True, location='headers')
    
    @login_required
    def post(self):
        """
        Logs out the current_user by invalidating their access_token

        Controller Functions Used:
            - logout

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        
        try:
            success = controllers.logout(access_token=args['access_token'], device_id=args['device_id'])
            return {'success': success}

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            return {'success': False}


class InstallRef(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('device_id', type=str, location='json', required=True, help=device_id_argument_help)
    post_parser.add_argument('url'      , type=str, location='json', required=True, help="url should be the refferal url")
    
    def post(self):
        """
        Install callback for logging a new install.

        Controller Functions Used:
            - install_ref

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            controllers.install_ref(args['device_id'], args['url'])
            return {'success':True}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class BadUsernames(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('timestamp', type=int, location='args', default=0, help="timestamp should be the UTC timestamp of the last time list of bad usernames was fetched.")
    
    def get(self):
        """
        Returns a list of bad usernames if the list has changed since provided timestamp or returns {"changed":false}
        bad usernames are usernames which are not allowed for the user

        Controller Functions Used:
            None

        Authentication: None
        """
        args = self.get_parser.parse_args()
        try:
            if args['timestamp'] < config.UNAVAILABLE_USERNAMES_LAST_UPDATED:
                return {'ulist':config.UNAVAILABLE_USERNAMES, 'changed':True}
            return {'ulist':[], 'changed':False}
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class VideoView(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('url', type=str, location='args', required=True)
    
    def get(self):
        """
        Redirects to the url provided in the argument.
        If the url is of a video, increments the view count of the video by 1.

        Controller Functions Used:
            - get_parser

        Authentication: None
        """
        
        args = self.get_parser.parse_args()
        try:
            from flask import redirect
            controllers.view_video(args['url'])
            return redirect(args['url'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            return redirect(args['url'])

class QuestionImageCreator(restful.Resource):
    
    def get(self, question_id):
        """
        Returns background image for a question.

        Controller Functions Used:
            - get_question_authors_image

        Authentication: None
        """
        try:
            from flask import send_file
            question_image = controllers.get_question_authors_image(question_id)

            return send_file(question_image, as_attachment=True, attachment_filename='%s.jpg'%(question_id))
        
        except CustomExceptions.ObjectNotFoundException as e:
            abort(404, message=str(e))

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class ContactUs(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', type=str, location ='json', required = True )
    post_parser.add_argument('email', type=str, location ='json', required = True )
    post_parser.add_argument('organisation', type=str, location ='json', required = True )
    post_parser.add_argument('message', type=str, location ='json', required = True )
    post_parser.add_argument('phone', type=str, location ='json', default = '000-000-0000')
    
    def post(self):
        """
        Lets user contact the frankly team.
        Stores message sent in the arguments.
        
        Controller Functions Used:
            - add_contact

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.add_contact(args['name'], args['email'], args['organisation'], args['message'], args['phone'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)      

class WebHiringForm(restful.Resource):
    
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name' , type=str, location='form', required=True)
    post_parser.add_argument('email', type=str, location='form', required=True)
    post_parser.add_argument('phone', type=str, location='form', default=None)
    post_parser.add_argument('role' , type=str, location='form', default=None)
    
    def post(self):
        """
        Updates a Google Sheet with the information provided.
        Made for hiring purposes.

        Controller Functions Used:
            - web_hiring_form

        Authentication: None
        """

        args = self.post_parser.parse_args()
        try:
            return controllers.web_hiring_form(args['name'], args['email'], args['phone'], args['role'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class InterviewVideoResource(restful.Resource):
    
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', type=int, location = 'args', default = 0)
    get_parser.add_argument('limit' , type=int, location = 'args', default = 10)
    
    def get(self):
        """
        Returns a list of media objects with video and their thumb urls.
        Made for hiring task purposes.

        Controller Functions Used:
            - interview_media_controller

        Authentication: None
        """
        args = self.get_parser.parse_args()
        try:
            return controllers.interview_media_controller(args['offset'], args['limit'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)  

class InviteCeleb(restful.Resource):
    
    invite_parser = reqparse.RequestParser()
    invite_parser.add_argument('invitable_id', type=str, location='json', required = True)
    
    @login_required
    def post(self):
        """
        Adds Invite for an Invitable by logged in user

        Controller Functions Used:
            - invite_celeb

        Authentication: Required
        """    
        args = self.invite_parser.parse_args()
        try:
            return controllers.invite_celeb(current_user.id, args['invitable_id'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class TopLikedUsers(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('count', type=int, location='args', default=5)

    @login_required
    def get(self):
        """
        Returns top users who are liked by the current user

        Controller Functions Used:
            - top_liked_users

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            return controllers.top_liked_users(current_user.id, count=args['count'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class FeedBackResponse(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('medium', type=str, location='json', required=True)
    post_parser.add_argument('message', type=str, location='json', required=True)
    post_parser.add_argument('X-Version-Code', dest='version_code', type=float, location='headers', default=0)

    @login_required
    def post(self):
        """
        Saves users feedback (y/n)

        Controller Functions Used:
            - save_feedback_response

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.save_feedback_response(current_user.id, args['medium'], args['message'], args['version_code'])
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)



class ChannelFeed(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('offset', type=int, location='args', default=0)
    get_parser.add_argument('limit', type=int, location='args', default=10)
    get_parser.add_argument('X-deviceid', type=str, location='headers')
    get_parser.add_argument('visit'  , type=int, default=0, location='args', help="visit should be the time difference of the current time and user's first visit in seconds for unauthorised requests")
    get_parser.add_argument('X-Version-Code', type=float, location='headers', default=0)
    get_parser.add_argument('append_top', type=str, location='args', default='')

    def get(self, channel_id):
        """
        Returns feed of the given channel_id

        Controller Functions Used:
            - get_channed_feed

        Authentication: Optional
        """
        args = self.get_parser.parse_args()
        try:

            current_user_id = None
            
            if current_user.is_authenticated():
                current_user_id = current_user.id                

            return controllers.get_channel_feed(current_user_id, channel_id, args['offset'], args['limit'], args['X-deviceid'], args['X-Version-Code'], args['append_top'], args['visit'])
        
        except CustomExceptions.BadRequestException as e:
            abort(404, message=str(e))
        except CustomExceptions.UserNotFoundException, e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)




class ChannelList(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('X-deviceid', type=str, location='headers')
    get_parser.add_argument('X-Version-Code', type=float, location='headers', default=0)

    @login_required
    def get(self):
        """
        Returns list of channel to be shown on remote screen

        Controller Functions Used:
            - get_channel_list

        Authentication: Required
        """
        args = self.get_parser.parse_args()
        try:
            return controllers.get_channel_list(current_user.id, args['X-deviceid'], args['X-Version-Code'])
        
        except CustomExceptions.BadRequestException as e:
            abort(404, message=str(e))
        except CustomExceptions.UserNotFoundException, e:
            abort(404, message=str(e))
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class AppVersion(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('device_type', type=str, location='args', choices=['android','ios'], required=True)
    get_parser.add_argument('device_version_code', type=int, location='args', required=True)

    def get(self):
        """
        Returns dictionary of latest app versions

        Controller Functions Used:
            - get_android_version_code

        Authentication: Optional
        """
        args = self.get_parser.parse_args()
        try:
            return controllers.check_app_version_code(args['device_type'],args['device_version_code'])
        
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class ReportAbuse(restful.Resource):

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('object_type', type=str, choices=['user', 'post', 'question'], location='json', required=True)
    post_parser.add_argument('object_id', type=str, location='json', required=True)
    post_parser.add_argument('reason', type=str, location='json', default=None)

    @login_required
    def post(self):
        """
        Logs an abuse report

        Controller Functions Used:
            - get_android_version_code

        Authentication: Required
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.report_abuse(current_user.id, args['object_type'], args['object_id'], args['reason'])
        
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class EncodeStatistics(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('count', type=int, location='args', default=20)
    
    def get(self):
        """
        Returns dictionary of latest app versions

        Controller Functions Used:
            - get_android_version_code

        Authentication: Optional
        """
        args = self.get_parser.parse_args()
        try:
            import video_db
            return video_db.get_encode_statictics(args['count'])
        
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class ArrowDirection(restful.Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('screen', type=str, location='args', required=True, choices=['profile', 'question_list', 'notifications', 'settings'], help="screen should be one of the following ['profile', 'question_list', 'notifications', 'settings']")

    def get(self):
        """
        Sends the direction of arrow to be shown on top left corner

        Authentication: Not Required
        """
        args = self.get_parser.parse_args()

        if args['screen'] in ['profile', 'notifications', 'settings']:
            return {'direction':'left'}
        else:
            return {'direction':'right'}


class BucketName(restful.Resource):

    def get(self):
        """
        Returns the name of the S3 bucket to upload the media

        Authentication: Not Required
        """
        return {'bucket_name':config.CURRENT_S3_BUCKET_NAME}



class RSS(restful.Resource):
    def get(self):
        """
        Returns RSS in xml form

        Controller Functions Used:
            - get_rss

        Authentication: Optional
        """
        try:

            resp = flask.make_response(controllers.get_rss())
            resp.headers['content-type'] = 'application/xml'
            return resp
        
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)

class ImageResizer(restful.Resource):

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('h', type=int, location='args', default=262)
    get_parser.add_argument('w', type=int, location='args', default=262)
    get_parser.add_argument('image_url', type=str, required=True, location='args')

    def get(self):
        """
        Returns resized image.

        Controller Functions Used:
            - get_resized_image

        Authentication: None
        """
        args = self.get_parser.parse_args()
        
        try:
            from flask import send_file
            resized_image = controllers.get_resized_image(args['image_url'], args['h'], args['w'])

            return send_file(resized_image, as_attachment=True, attachment_filename='image.jpeg')

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message=internal_server_error_message)


class UserContactsUpload(restful.Resource):
    @login_required
    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('uploaded_file', type=file, required=True, location='files')
        post_parser.add_argument('X-Deviceid', type=str, required=True, location='headers', dest='device_id')

        args = post_parser.parse_args()
        try:
            resp = controllers.contact_file_upload(current_user.id, args['uploaded_file'], args['device_id'])
            return {'success': True, 'resp':resp}
        
        except CustomExceptions.BadFileFormatException as e:
            print traceback.format_exc(e)
            abort(400, message='File format not allowed')
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message='upload failure')

class RegisterBadEmail(restful.Resource):

    post_parser = reqparse.RequestParser()
    
    post_parser.add_argument('email'         , type=str, required=True, location='json')
    post_parser.add_argument('reason_type'   , type=str, required=True, location='json')
    post_parser.add_argument('reason_subtype', type=str, required=True, location='json')

    def post(self):
        """
        Registers an email in bad_emails table.

        Controller Functions Used:
            -register_bad_email

        Authentication: None
        """
        args = self.post_parser.parse_args()
        try:
            return controllers.register_bad_email(email         = args['email'],
                                            reason_type = args['reason_type'],
                                            reason_subtype = args['reason_subtype']
                                            )
        except Exception as e:
            print traceback.format_exc(e)
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            abort(500, message=internal_server_error_message)            

class ReceiveSNSNotifications(restful.Resource):

    
    def post(self):
        """
        Receives notifications from aws SNS.

        Controller Functions Used:
            -register_bad_email

        Authentication: None
        """
        try:
            notification = json.loads(request.data)
            message = json.loads(notification['Message'])
            email = message['mail']['destination'][0]
            notification_type = message['notificationType']

            if notification_type == 'Bounce':
                if message['bounce']['bounceType'] in ['Permanent', 'Transient']:
                    bounce_sub_type = message['bounce']['bounceSubType']
                    return controllers.register_bad_email(email=email, reason_type=notification_type, reason_subtype=bounce_sub_type)
            if notification_type == 'Complaint':
                complaint_feedback_type = message['complaint']['complaintFeedbackType']
                return controllers.register_bad_email(email=email, reason_type=notification_type, reason_subtype=complaint_feedback_type)
            return {'success':'false', 'email':email, 'reason':'Not a bad email'}

        except Exception as e:
            print traceback.format_exc(e)
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])
            with open('data.txt', 'w') as outfile:
                json.dump(request.data, outfile)
            abort(500, message=internal_server_error_message)


class PublicDocumentation(restful.Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('doc_key', type=str, location='args', required=True)
    def get(self):
        args = self.get_parser.parse_args()
        if args['doc_key'] == 'AFfbe394002dde':
            from flask import render_template
            import json
            with open("newcontextdict") as infile :
                newcontext = json.load(infile)  
            #return Response(json.dumps(doc_gen(app, resources)), content_type='application/json')
            resp = flask.make_response(render_template('api_docnew.html', endpoints=newcontext))
            resp.headers['content-type'] = 'text/html'
            return resp
        else:
            abort(403, message='Ra Ra Rasputin says: You are are hitting a wrong url.')

