import requests

def get_gplus_data(access_token):
	headers = {'Content-Type': 'application/json',
				'Authorization': 'OAuth ' + access_token}
	res = requests.get(
		'https://www.googleapis.com/plus/v1/people/me', headers=headers)
	print res.status_code
	if res.status_code == 200:
		data = res.json()
		user_data = {
				'social_id': data.get('id'),
				'first_name': data.get('name').get('givenName') if data.get('name') else None,
				'last_name': data.get('name').get('familyName') if data.get('name') else None,
				'email': data.get('emails')[0]['value'] if data.get('emails')[0]['value'] else None
			}
		user_data['profile_picture'] = data.get('image',{}).get('url',None)
		if user_data['first_name'] and user_data['last_name']:
			user_data['full_name'] = user_data['first_name'] + " " + user_data['last_name']
		elif user_data['first_name']:
			user_data['full_name'] = user_data['first_name']
		elif user_data['first_name']:
			user_data['full_name'] = user_data['first_name']
		else:
			user_data['full_name'] = None
		user_data['gender'] = 'M' if data.get('gender') == 'male' else 'F'
		return user_data
	else:
		raise Exception("gplus status code"+res.status_code)