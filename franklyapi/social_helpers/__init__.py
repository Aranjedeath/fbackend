from facebook_helpers import get_fb_data, get_extended_graph_token, get_fb_permissions
from twitter_helpers import get_twitter_data
from gplus_helpers import get_gplus_data


def get_user_data(social_type, access_token, access_secret=None):
	if social_type == 'facebook':
		return get_fb_data(access_token)
	
	elif social_type == 'twitter' and access_secret:
		return get_twitter_data(access_token, access_secret)

	elif social_type == 'google':
		return get_gplus_data(access_token)

def check_for_write_permission(social_type, access_token, access_secret=None):
    if social_type == 'facebook':
        pass
    elif social_type == 'twitter' and access_secret:
        pass
    elif social_type == 'google':
        pass
