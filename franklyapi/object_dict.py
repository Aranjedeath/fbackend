import time


def location_dict(lat, lon, location_name, country_name, country_code):
    return {
            'lat':lat,
            'lon':lon,
            'location_name':location_name,
            'country_name':country_name,
            'country_code':country_code
            }

def user_to_dict(user):
    from app import ADMIN_USERS
    from controllers import get_follower_count, get_following_count, get_answer_count, get_user_like_count
    user_dict = {
        'id': str(user.id).zfill(24),
        'email': user.email,
        'username': user.username,
        'facebook_id': user.facebook_id,
        'twitter_id': user.twitter_id,
        'instagram_id': user.twitter_id,
        'google_id': user.google_id,
        'first_name': user.first_name,
        'last_name': None,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'cover_picture': user.cover_picture,
        'profile_video': user.profile_video,
        'gender': user.gender,
        'follower_count': get_follower_count(user.id),
        'following_count': get_following_count(user.id),
        'answer_count': get_answer_count(user.id),
        'likes_count': get_user_like_count(user.id),
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'last_updated': int(time.mktime(user.last_updated.timetuple())),
        'fb_perm' : str(user.facebook_token_type),
        'admin_level':1 if user.id in ADMIN_USERS else 0,
        
        'user_type':user.user_type,
        'user_title':user.user_title,
    }
    return user_dict


def guest_user_to_dict(user, current_user=None, cur_user_interest_tags=None):
    from controllers import get_follower_count, get_following_count, get_answer_count,\
                            get_user_like_count, is_follower, is_following, get_user_view_count
    if user.deleted == True:
        return thumb_user_to_dict(user)
    user_dict = {
        'id': str(user.id).zfill(24),
        'username': user.username,
        'first_name': user.first_name,
        'last_name': None,
        'bio': user.bio,
        'profile_picture': user.profile_picture,
        'cover_picture': user.cover_picture,
        'profile_video': user.profile_video,
        'gender': user.gender,
        'follower_count': get_follower_count(user.id),
        'following_count': get_following_count(user.id),
        'answer_count': get_answer_count(user.id),
        'likes_count': get_user_like_count(user.id),
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'is_follower':is_follower(user.id, current_user.id) if current_user else False,
        'is_following':is_following(user.id, current_user.id) if current_user else False,
        'allow_anonymous_question': user.allow_anonymous_question,
        'view_count' : get_user_view_count(user.id),
        'user_type':user.user_type,
        'user_title':user.user_title
    }
    
    return user_dict

def thumb_user_to_dict(user):
    user_dict = {
        'id':str(user.id).zfill(24),
        'username': user.username,
        'first_name': user.first_name,
        'last_name': None,
        'profile_picture': user.profile_picture,
        'deleted': user.deleted,
        'gender':user.gender,
        'bio' : user.bio,
        'allow_anonymous_question' : user.allow_anonymous_question,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'user_title':user.user_title
    }
    return user_dict


