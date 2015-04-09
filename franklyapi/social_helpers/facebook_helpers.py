import facebook
import requests
import datetime

import os,sys,inspect


#parent directory hack
try:
    from configs import config
except:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from configs import config

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

def get_facebook_long_lived_token(short_lived_token):
    params = {
        'grant_type': 'fb_exchange_token',
        'client_secret': config.FACEBOOK_APP_SECRET,
        'client_id': config.FACEBOOK_APP_ID,
        'fb_exchange_token': short_lived_token
    }
    try:
        resp = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        if resp.status_code==200:
            # print resp.content
            return resp.content.split('&')[0].split('=')[1]
        else:
            raise Exception('Something Went wrong with the request')
    except:
        return short_lived_token

def get_fb_data(access_token):
    access_token = get_facebook_long_lived_token(access_token)
    graph = facebook.GraphAPI(access_token)
    profile = graph.get_object("me")
    
    user_data = {}

    user_data['social_id']       = profile['id']
    user_data['email']           = profile['email'] if profile.get('email') else '{username}@facebook.com'.format(username=profile.get('username', profile['id']))
    user_data['full_name']       = profile.get('name', profile['first_name']+' '+profile.get('last_name', '')).strip()
    user_data['gender']          = 'M' if profile.get('gender')=='male' else 'F' if profile.get('gender')=='femaile' else None
    user_data['bio']             = profile['about'].replace('\n', ' ') if profile.get('about') else None
    user_data['location_name']   = profile['location']['name'] if profile.get('location') and profile.get('location').get('name') else None
    user_data['birthday']        = datetime.datetime.strptime(profile['birthday'], '%m/%d/%Y') if profile.get('birthday') else None

    user_data['profile_picture'] = get_facebook_profile_picture(user_data['social_id'])

    return user_data

if __name__ == '__main__':    
    short_token = 'CAALdknmm9gQBAPVOJ3ceJiEDv6pBlV49ayQcZCpVkB7ZBAXZASm9uClOYSPSI43lWNurdTMMwdssjDksE5Ld9FEBpi29jRTqgthNNR1jVXFcXfqph9q8ffaeghzZB8OUdiSErRx6IMPij1Y7phKObLQ73qUhZAGNaPOviDMH6Vfyx1VStuYTb6LmVMfiVm31u65NGX16SWDc7QmyLzjYBV2oAZBBmRYOQXZC5MtZCtU3FgZDZD'
    print get_facebook_long_lived_token(short_token)