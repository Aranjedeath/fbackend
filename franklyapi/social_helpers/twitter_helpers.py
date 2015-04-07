import twitter
from configs import config
import traceback

app_token = config.TWITTER_APP_TOKEN
app_secret = config.TWITTER_APP_SECRET

def is_not_twitter_default_image(url):
	return not 'default_profile_images' in url

def get_twitter_data(access_token, access_secret, app_token=app_token,app_secret=app_secret):
	try:
		api = twitter.Api(app_token,app_secret,access_token,access_secret)
		tuser = api.VerifyCredentials()
		user_data = {}
		if(tuser):
			user_data['social_id'] = tuser.id if tuser.id else None
			user_data['full_name'] = tuser.name if tuser.name else None
			user_data['profile_picture'] = tuser.profile_image_url if tuser.profile_image_url and is_not_twitter_default_image(tuser.profile_image_url) else None
			user_data['location_name'] = tuser.location if tuser.location else None
			user_data['bio'] = tuser.description if tuser.description else None
		return user_data
	except Exception as e:
		print traceback.format_exc(e)
		raise e
