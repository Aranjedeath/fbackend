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

# def get_facebook_long_lived_token(short_lived_token):
#     params = {
#         'grant_type': 'fb_exchange_token',
#         'client_secret': config.FACEBOOK_APP_SECRET,
#         'client_id': config.FACEBOOK_APP_ID,
#         'fb_exchange_token': short_lived_token
#     }
#     try:
#         resp = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
#         if resp.status_code==200:
#             # print resp.content
#             return resp.content.split('&')[0].split('=')[1]
#         else:
#             raise Exception('Something Went wrong with the request')
#     except:
#         return short_lived_token

def get_extended_graph_token(short_access_token):
    graph = facebook.GraphAPI(access_token)
    try:
        resp = graph.extend_access_token(config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET)
        extended_token = resp.get('access_token')
    except exception as e:
        return short_access_token
    return extended_token

def get_fb_data(access_token):
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

def get_fb_permissions(access_token):
    """
    takes in a facebook access token
    returns a set of all facebook access permissions.
    """
    permission_url = "https://graph.facebook.com/me/permissions?access_token={0}".format(access_token)
    print "hit url", permission_url
    resp = requests.get(permission_url, allow_redirects=False)
    print resp.json()
    allowed_permissions = set()
    if resp.status_code == 200:
        resp_data = resp.json()['data']
        print type(resp_data)
        for item in resp_data:
            if item.get('status') == 'granted':
                allowed_permissions.add(item.get('permission'))
    return allowed_permissions

if __name__ == '__main__':    
    short_token = 'CAACEdEose0cBABZC9k67eQo192ZCTLKKmqQw6vKiZBzswRZBHEUqxvcxkJIYYSRBNS6DmEKUNixw7t4glwqoBZBPCJb3nE2PVXwrxx0HHrlQrxgFMML9BdnvFKymyaKprezzfvvy6EXC2y28jtBu5CE8RWT3PrBfzOuXjbGZBzOAf2c9ZBhYZB3cHY6gNRqOmX72WxMhO8djBVJjeVcrI6OR'
    # print get_fb_data(short_token)
    print get_fb_permissions(short_token)