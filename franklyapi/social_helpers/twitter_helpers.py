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

def get_twitter_permissions(token, secret):
	from requests_oauthlib import OAuth1Session
	url = 'https://api.twitter.com/1.1/account/settings.json'
	twitter_oauth = OAuth1Session(app_token, client_secret=app_secret,
                            	resource_owner_key=token,
                            	resource_owner_secret=secret)
	r = twitter_oauth.get(url)
	print r.status_code
	if r.status_code != 200:
		raise Exception('twitter api status code: %s' %r.status_code)
	permissions_list = r.headers['x-access-level'].split('-')
	return permissions_list

def check_twitter_write_permission(token, secret):
	try:
		permissions_list = get_twitter_permissions(token, secret)
		return 'write' in permissions_list
	except:
		return False

def publish_to_twitter(token, secret, link):
	api = twitter.Api(app_token,app_secret,access_token,access_secret)
	api.PostUpdate('I just answered a question on frankly! %s' %link)


