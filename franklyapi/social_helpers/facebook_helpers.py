import facebook
import traceback
import requests
import json

def get_profile_picture(fb_id):
    try:
        url = 'https://graph.facebook.com/%s/picture?type=large&redirect=false' % (fb_id)
        res = requests.get(url, allow_redirects=False)
        if res.status_code == 200:
           #pic_url = pic_url.replace('s.jpg', 'n.jpg')
           #pic_url = pic_url.replace('50.50','480.480')
           #pic_url = pic_url.replace('p50x50','p480x480')
            res_json = res.json()
            if(res_json['data']['url'] and (not res_json['data']['is_silhouette'])):
                print res_json['data']['url']
                return res_json['data']['url']
            # if res.get('is_silhouette'):
            #     res = requests.get(res.get('url',''))
            #     print res
            #     if res.status_code == 200:
            #         return url
        return False
    except Exception as e:
        print e
        return False

def get_fb_data(access_token):
    try:
        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object("me")
        user_data = {
            'social_id' : profile.get('id'),
            'email' : profile.get('email', '{username}@facebook.com'.format(username=profile['username']))
        }
        if (profile.get('name')):
            user_data['full_name'] = profile.get('name')
        else:
            user_data['full_name'] = None
        if(profile.get('gender') == 'male'):
            user_data['gender'] = 'M'
        else:
            user_data['gender'] = 'F'
        
        if(profile.get('about')):
            user_data['bio'] = str(profile.get('about')).replace('\n',' ')
        else:
            user_data['bio'] = None
        if profile.get('location') and profile.get('location').get('name'):
            user_data['location_name'] = profile.get('location').get('name')
        pic = get_profile_picture(user_data['social_id'])
        #pic = graph.get_object("me/picture?type=large")
        if(pic):
            user_data['profile_picture'] = pic
        else:
            user_data['profile_picture'] = None
        print user_data
        return user_data
    except Exception as e:
        print traceback.format_exc(e)
        raise e