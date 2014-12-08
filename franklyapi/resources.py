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



class UserUpdateForm(restful.Resource):
    @login_required
    def post(self, user_id):

        user_update_profile_form = reqparse.RequestParser()
        user_update_profile_form.add_argument('first_name', type=str, location='form')
        user_update_profile_form.add_argument('bio', type=str, location='form')
        user_update_profile_form.add_argument('profile_picture', location='files')
        user_update_profile_form.add_argument('cover_picture', location='files')
        user_update_profile_form.add_argument('profile_video', location='files')

        args = user_update_profile_form.parse_args()
               
        try:
            user_id = int(user_id)
            if user_id == 'me':
                user_id = current_user.id
            
            if (str(current_user.id) not in config.ADMIN_USERS) and user_id != current_user.id:
                raise CustomExceptions.NoPermissionException()
            
            new_profile = controllers.user_update_profile_form(user_id, **args)
            
            return new_profile

        except CustomExceptions.BadRequestException, e:
            print traceback.format_exc(e)
            abort(400, message=str(e))

        except CustomExceptions.UserNotFoundException, e:
            abort(403, message='Unauthorised')

        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0],err[1],err[2])
            print traceback.format_exc(e)
            abort(500, message="Internal Server Error")


class UserProfile(restful.Resource):

    def get(self, user_id):
        try:
            username = None
            if not user_id.isdigit() and not user_id == 'me':
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





