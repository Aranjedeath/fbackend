import requests

def get_gplus_data(access_token):
    headers = {
                'Content-Type': 'application/json',
                'Authorization': 'OAuth ' + access_token
                }
    res = requests.get('https://www.googleapis.com/plus/v1/people/me', headers=headers)
    
    if res.status_code == 200:
        data = res.json()
        user_data = {
                'social_id': data['id'],
                'first_name': data['name'].get('givenName') if data.get('name') else None,
                'last_name': data['name'].get('familyName') if data.get('name') else None,
            }
        email = None
        for email_objects in data['emails']:
            email = email_objects['value']
            if email:
                break
        user_data['email'] = email
        user_data['profile_picture'] = data.get('image',{}).get('url',None) if (data.get('image',{}) and (not data.get('image',{}).get('isDefault'))) else None
        
        if user_data['first_name'] and user_data['last_name']:
            user_data['full_name'] = user_data['first_name'] + " " + user_data['last_name']
        elif user_data['first_name']:
            user_data['full_name'] = user_data['first_name']
        else:
            user_data['full_name'] = None
        user_data['gender'] = 'M' if data.get('gender') == 'male' else 'F' if data.get('gender') == 'female' else None
        return user_data
    else:
        raise Exception("Google Plus status_code :%s\nServer resp: %s" %(res.status_code, res.json()))

def get_gplus_permissions(access_token):
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'%access_token
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception('GPlus status code: %s' %resp.status_code)
    permissions = resp.json()['scope'].split()
    permissions = map(lambda x: x.replace('https://www.googleapis.com/auth/', ''), permissions)
    return permissions
    