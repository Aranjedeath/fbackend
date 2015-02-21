import facebook
import requests
import datetime

def get_facebook_profile_picture(facebook_id):
    try:
        url = 'https://graph.facebook.com/{facebook_id}/picture?type=large&redirect=false'.format(facebook_id=facebook_id)
        response = requests.get(url, allow_redirects=False)
        
        if response.status_code == 200:
            response_data = response.json()['data']
            if response_data['url'] and not response_data['is_silhouette']:
                return response_data['url']
        return False
    except:
        return False


def get_fb_data(access_token):
    graph = facebook.GraphAPI(access_token)
    profile = graph.get_object("me")
    
    user_data = {}

    user_data['social_id']       = profile['id'],
    user_data['email']           = profile['email'] if profile.get('email') else '{username}@facebook.com'.format(username=profile.get('username', profile['id']))
    user_data['full_name']       = profile.get('name', profile['first_name']+profile.get('last_name', ''))
    user_data['gender']          = 'M' if profile.get('gender')=='male' else 'F' if profile.get('gender')=='femaile' else None
    user_data['bio']             = profile['about'].replace('\n', ' ') if profile.get('about') else None
    user_data['location_name']   = profile['location']['name'] if profile.get('location') and profile.get('location').get('name') else None
    user_data['birthday']        = datetime.datetime.strptime(profile['birthday'], '%m/%d/%Y') if profile.get('birthday') else None

    user_data['profile_picture'] = get_facebook_profile_picture(user_data['social_id'])

    return user_data