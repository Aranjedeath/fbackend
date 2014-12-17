import facebook
import traceback

def get_fb_data(access_token):
	try:
		graph = facebook.GraphAPI(access_token)
		profile = graph.get_object("me")
		user_data = {
			'social_id' : profile.get('id'),
			'email' : profile.get('email')
		}
		if (profile.get('name')):
			user_data['full_name'] = profile.get('name')
		else:
			user_data['full_name'] = None
		if(profile.get('gender') == 'male'):
			user_data['gender'] = 'M'
		else:
			user_data['gender'] = 'F'
		
		if(profile.get('bio')):
			user_data['bio'] = str(profile.get('bio')).replace('\n',' ')
		else:
			user_data['bio'] = None
		if profile.get('location') and profile.get('location').get('name'):
			user_data['location_name'] = profile.get('location').get('name')
		#pic = graph.get_object("me/picture?type=large")
		#if(pic['url']):
		#	user_data['profile_picture'] = pic['url']
		#else:
		#	user_data['profile_picture'] = None
		return user_data
	except Exception as e:
		print traceback.format_exc(e)
		raise e()