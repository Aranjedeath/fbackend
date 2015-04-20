from facebook_helpers import get_fb_data, get_extended_graph_token, get_fb_permissions, check_publish_permission, publish_to_facebook
from twitter_helpers import get_twitter_data, check_twitter_write_permission
from gplus_helpers import get_gplus_data, check_gplus_write_permission
from models import Post, User



def get_user_data(social_type, access_token, access_secret=None):
	if social_type == 'facebook':
		return get_fb_data(access_token)
	
	elif social_type == 'twitter' and access_secret:
		return get_twitter_data(access_token, access_secret)

	elif social_type == 'google':
		return get_gplus_data(access_token)

def check_for_write_permission(social_type, access_token, access_secret=None):
    if social_type == 'facebook':
        return bool(check_publish_permission(access_token))
    elif social_type == 'twitter' and access_secret:
        return check_twitter_write_permission(access_token, access_secret)
    elif social_type == 'google':
        return check_gplus_write_permission(access_token)
    else:
        raise Exception('invalid social_type')

def share_post(post_id, user_id, post_to_facebook, post_to_twitter):
    user = User.query.filter(User.id==user_id).one()
    post = Post.query.filter(Post.id==user_id).one()
    question = Question.query.filter(Question.id==post.question).one()
    link = 'frankly.me/p/%s' %post.client_id
    if post_to_facebook:
        publish_to_facebook(message="I just answered a question on Frankly.me", post_name='Frankly.me', post_link=link, post_caption='Frankly', 
                            post_description="Shashank's answer to '%s'" %question.body,
                            access_token=user.facebook_token)
    if post_to_twitter:
        publish_to_twitter(token=user.twitter_token, secret=user.twitter_secret
                            link=link)

