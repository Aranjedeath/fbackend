import os
import random
import datetime
import time
import hashlib
import uuid
import traceback
import sys
import json

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.sql import text

import CustomExceptions
import media_uploader
import async_encoder
import social_helpers
import util






from configs import config
from configs import flag_words
from models import User, Block, Follow, Like, Post, UserArchive, AccessToken,\
                    Question, Upvote, Comment, ForgotPasswordToken, Install, Video,\
                    UserFeed, Event, Reshare, Invitable, Invite, ContactUs, InflatedStat,\
                    IntervalCountMap, ReportAbuse, SearchCategory,\
                    BadEmail, List, ListItem, ListFollow, DiscoverList

from notification import notification_decision, make_notification as notification

from app import redis_client, raygun, db, redis_views, redis_pending_post

from object_dict import user_to_dict, guest_user_to_dict,\
                        thumb_user_to_dict, question_to_dict,questions_to_dict, post_to_dict, comment_to_dict,\
                        comments_to_dict, posts_to_dict, make_celeb_questions_dict, media_dict,invitable_to_dict, guest_users_to_dict

from video_db import add_video_to_db
from database import get_item_id
from trends import most_liked_users

from mail import make_email



def create_event(user, action, foreign_data, event_date=datetime.date.today()):
    if not Event.query.filter(Event.user==user, Event.action==action, Event.foreign_data==foreign_data, Event.event_date==event_date).count():
        return Event(user=user, action=action, foreign_data=foreign_data, event_date=event_date)
    return



def check_access_token(access_token, device_id):
    start = datetime.datetime.now()
    try:
        print access_token, device_id
        device_type = get_device_type(device_id)
        user = None
        
        if device_type == 'web':
            user_id = redis_client.get(access_token)
            user = User.query.filter(User.id==user_id).first()

        else:
            user = User.query.join(AccessToken, AccessToken.user==User.id
                                            ).filter(AccessToken.access_token==access_token,
                                                        AccessToken.device_id==device_id,
                                            ).first()

        return user
    
    except Exception as e:
        err = sys.exc_info()
        raygun.send(err[0],err[1],err[2])
        print traceback.format_exc(e)
        raise e

def password_is_valid(password):
    if len(password)<6:
        return False
    return True


def email_available(email):
    if email.split('@')[1].lower() in config.BLOCKED_EMAIL_DOMAINS:
        return False
    return not bool(User.query.filter(User.email==email).count())


def username_available(username):
    if len(username)<6 or len(username)>30 or username in config.UNAVAILABLE_USERNAMES:
        return False
    for char in username:
        if char not in config.ALLOWED_CHARACTERS:
            return False
    return not bool(User.query.filter(User.username==username).count())


def sanitize_username(username):
    username = username.title().replace(' ', '')
    for char in username:
        if char not in config.ALLOWED_CHARACTERS:
            username = username.replace(char, '') 
    return username 


def make_username(email, full_name=None, social_username=None):
    username_candidates = [full_name, social_username, email.split('@')[0]]
    for item in username_candidates:
        if item:
            sanitized_item = sanitize_username(item)
            if username_available(sanitized_item):
                return sanitized_item
    
    for item in username_candidates:
        if item:
            sanitized_item = sanitize_username(item) + str(random.randint(1, 9999))
            if username_available(sanitized_item):
                return sanitized_item

    suffix = random.choice(['red', 'big', 'small', 'pink', 'thin', 'smart', 'genius', 'black', 'evil', 'purple'])
    prefix = random.choice(['tomato', 'potato', 'cup', 'rabbit', 'bowl', 'book', 'ball', 'wall', 'chocolate'])
    
    uname_valid = False
    while not uname_valid:
        username = '%s_%s'%(suffix,prefix)
        uname_valid = username_available(username)
        username = username+str(random.randint(0, 9999))
    return username


def make_password():
    suffix = random.choice(['red', 'big', 'small', 'pink', 'thin', 'smart', 'genius', 'black', 'evil', 'purple'])
    prefix = random.choice(['tomato', 'potato', 'cup', 'rabbit', 'bowl', 'book', 'ball', 'wall', 'chocolate'])
    password = random.choice(suffix) + random.choice(prefix) + str(random.randint(0, 10000))
    return password

def generate_access_token(user_id, device_id=None):
    return hashlib.sha1('%s%s' % (user_id, int(time.time()))).hexdigest()


def set_access_token(device_id, device_type, user_id, access_token, push_id=None):
    from app import redis_client
    if device_type == 'web':
        redis_client.setex(access_token, str(user_id), 3600*24*10)
        return
    db.session.execute(text("""INSERT INTO access_tokens (access_token, user, device_id, device_type, active, push_id, last_login) 
                                VALUES(:access_token, :user_id, :device_id, :device_type, true, :push_id, :last_login) 
                                ON DUPLICATE KEY 
                                UPDATE access_token=:access_token, user=:user_id, active=true, push_id=:push_id, last_login=:last_login"""
                                ),
                        params={'device_id':device_id, 'device_type':device_type ,'access_token':access_token, 'user_id':user_id, 'push_id':push_id, 'last_login':datetime.datetime.now()}
                        )
    db.session.commit()


def get_data_from_external_access_token(social_type, external_access_token, external_token_secret=None):
    from twitter import TwitterError
    try:
        user_data = social_helpers.get_user_data(social_type, external_access_token, external_token_secret)
        return user_data
    except TwitterError as e:
        raise CustomExceptions.InvalidTokenException(str(e))


def get_user_from_social_id(social_type, social_id):
    user = None
    if social_type == 'facebook':
        user = User.query.filter(User.facebook_id==social_id).first()
    elif social_type == 'google':
        user = User.query.filter(User.google_id==social_id).first()
    elif social_type == 'twitter':
        user = User.query.filter(User.twitter_id==social_id).first()
    return user

def get_device_type(device_id):
    if len(device_id)<17:
        if 'web' in device_id:
            return 'web'
        return 'android'
    return 'ios'


def send_registration_mail(user_id, mail_password=False):
    user = User.query.get(user_id)
    if 'twitter' not in user.registered_with:
        make_email.welcome_mail(user_id=user.id)


def new_registration_task(user_id, mail_password=True):
    # add any task that should be done for a first time user
    if mail_password:
        send_registration_mail(user_id, mail_password=mail_password)


def register_email_user(email, full_name, device_id, password=None, username=None, phone_num=None,
                        push_id=None, gender=None, user_type=0, user_title=None, 
                        lat=None, lon=None, location_name=None, country_name=None, country_code=None,
                        bio=None, profile_picture=None, profile_video=None, admin_upload=False,
                        added_by=None, IP_address=None):
    
    if not email_available(email):
        raise CustomExceptions.UserAlreadyExistsException("A user with that email already exists")

    if username and not username_available(username):
        raise CustomExceptions.UserAlreadyExistsException("A user with that username already exists")
    elif not username:
        username = make_username(email, full_name)

    device_type = get_device_type(device_id)
    registered_with = device_type + '_email'
    mail_password = False
    if not password:
        mail_password = True
        password=make_password
        registered_with = 'auto'+registered_with

    new_user = User(email=email, username=username, first_name=full_name, password=password, 
                    registered_with=registered_with, user_type=user_type, gender=gender, user_title=user_title,
                    phone_num=phone_num, lat=lat, lon=lon, location_name=location_name, country_name=country_name,
                    country_code=country_code, bio=bio, id=get_item_id(), added_by=added_by)
    
    db.session.add(new_user)
    db.session.commit()
    
    if profile_picture or profile_video:
        user_update_profile_form(new_user.id, profile_picture=profile_picture, profile_video=profile_video, moderated_by=added_by)

    access_token=None
    if not admin_upload:
        access_token = generate_access_token(new_user.id, device_id)
        set_access_token(device_id, device_type, new_user.id, access_token, push_id)
    
    new_registration_task(new_user.id, mail_password=mail_password)


    return {'access_token':access_token, 'username':username,
            'id':new_user.id, 'new_user':True, 'user_type':new_user.user_type,
            'user':user_to_dict(new_user)
            }

def get_twitter_email(twitter_id):
    return '{twitter_id}@twitter.com'.format(twitter_id=twitter_id)


def login_user_social(social_type, social_id, external_access_token, device_id, push_id=None, 
                        external_token_secret = None, user_type=0, user_title=None):
    user_data = get_data_from_external_access_token(social_type, external_access_token, external_token_secret)
    token_valid = str(user_data['social_id']).strip()==str(social_id).strip()
    
    if not token_valid:    
        raise CustomExceptions.InvalidTokenException("Could not verify %s token"%social_type)

    user = get_user_from_social_id(social_type, social_id)
    device_type = get_device_type(device_id)

    update_dict = {'deleted':False, '%s_token'%(social_type):external_access_token, '%s_id'%(social_type):social_id}

    if social_type == 'twitter':
        update_dict.update({'twitter_secret':external_token_secret})
        user_data['email'] = get_twitter_email(user_data['social_id'])
        user_data['social_id'] = str(user_data['social_id']).strip()
        user = User.query.filter(User.twitter_id==user_data['social_id']).first()

    existing_user = None
    if social_type in ['facebook', 'google']:
        existing_user = User.query.filter(User.email==user_data['email']).first()

    if existing_user and not user:
        user = existing_user

    if user:
        access_token = generate_access_token(user.id, device_id)
        set_access_token(device_id, device_type, user.id, access_token, push_id)
        activated_now=user.deleted
        User.query.filter(User.id==user.id).update(update_dict)
        db.session.commit()
        return {'access_token': access_token, 'id':user.id,
                'username':user.username, 'activated_now': activated_now,
                'new_user' : False, 'user_type' : user.user_type,
                'user':user_to_dict(user)
                }
    
    else:
        username = make_username(user_data['email'], user_data.get('full_name'), user_data.get('social_username'))
        
        registered_with = '%s_%s'%(device_type, social_type)

        new_user = User(email=user_data['email'], username=username, first_name=user_data['full_name'], 
                        registered_with=registered_with, user_type=user_type, gender=user_data.get('gender'), user_title=user_title,
                        location_name=user_data.get('location_name'), country_name=user_data.get('country_name'),
                        country_code=user_data.get('country_code'))
        
        if user_data.get('profile_picture'):
            new_user.profile_picture = media_uploader.upload_user_image(user_id=new_user.id, 
                                                        image_url=user_data['profile_picture'], 
                                                        image_type='profile_picture')
        
        if social_type == 'facebook':
            new_user.facebook_id = social_id
            new_user.facebook_token = external_access_token
        elif social_type == 'twitter':
            new_user.twitter_id = social_id
            new_user.twitter_token = external_access_token
            new_user.twitter_secret = external_token_secret
        elif social_type == 'google':
            new_user.google_id = social_id
            new_user.google_token = external_access_token

        db.session.add(new_user)
        db.session.commit()
        access_token = generate_access_token(new_user.id, device_id)
        set_access_token(device_id, device_type, new_user.id, access_token, push_id)
        new_registration_task(new_user.id)

        return {'access_token': access_token, 'id':new_user.id,
                'username':new_user.username, 'activated_now':False,
                'new_user' : True, 'user_type': new_user.user_type,
                'user':user_to_dict(new_user)
                } 

def login_email_new(user_id, id_type, password, device_id, push_id=None):
    try:
        if id_type=='email':
            user = User.query.filter(User.email==user_id, User.password==password).one()
        elif id_type=='username':
            user = User.query.filter(User.username==user_id, User.password==password).one()
        else:
            raise Exception("id_type should be in ['email', 'username']")
        if not user:
            raise NoResultFound()
        
        access_token = generate_access_token(user.id, device_id)
        device_type = get_device_type(device_id)
        set_access_token(device_id, device_type, user.id, access_token, push_id)
        activated_now = user.deleted
        if activated_now:
            User.query.filter(User.id==user.id).update({'deleted':False})
        return {'access_token': access_token, 'username': user.username,
                'activated_now': activated_now, 'id':user.id,
                'new_user':False, 'user_type' : user.user_type,
                'user':user_to_dict(user)
                }
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException("No user with the given %s found"%(id_type))


def has_blocked(cur_user_id, user_id):
    return bool(Block.query.filter(or_(Block.user==cur_user_id, Block.blocked_user==cur_user_id)).filter(Block.user==user_id, Block.blocked_user==user_id).limit(1).count())


def question_count(user_id):
    question_count = Question.query.filter(Question.question_to==user_id,
                            Question.deleted==False,
                            Question.is_answered==False,
                            Question.is_ignored==False
                            ).count()
    return {'question_count':question_count}




def get_posts_stats(post_ids, cur_user_id=None):
    results = db.session.execute(text("""SELECT posts.id, posts.view_count,
                                            (SELECT count(1) FROM post_likes 
                                                WHERE post_likes.post=posts.id 
                                                    AND post_likes.unliked=false) AS like_count,
                                            
                                            (SELECT count(1) FROM comments
                                                WHERE comments.on_post=posts.id
                                                AND comments.deleted=false) AS comment_count,
                                            
                                            (SELECT count(1) FROM post_likes 
                                                WHERE post_likes.post=posts.id
                                                    AND post_likes.user=:cur_user_id
                                                    AND post_likes.unliked=false) AS is_liked,

                                            (SELECT count(1) FROM post_shares
                                                WHERE post_shares.post=posts.id
                                                    AND post_shares.platform='whatsapp') as whatsapp_share_count,
                                            
                                            (SELECT count(1) FROM post_shares
                                                WHERE post_shares.post=posts.id
                                                    AND post_shares.platform!='whatsapp') as other_share_count
                                        
                                        FROM posts
                                        WHERE posts.id in :post_ids"""),
                                    params = {'post_ids':list(post_ids), 'cur_user_id':cur_user_id}
                                )
    
    data = {}
    for row in results:
        data[row[0]] = {'view_count':row[1],
                        'like_count':row[2],
                        'comment_count':row[3],
                        'is_liked':bool(row[4]),
                        'whatsapp_share_count':row[5],
                        'other_share_count':row[6]
                        }

    inflated_stats = InflatedStat.query.filter(InflatedStat.post.in_(post_ids)).all()
    for inflated_stat in inflated_stats:
        data[inflated_stat.post]['view_count'] += inflated_stat.view_count
        data[inflated_stat.post]['like_count'] += inflated_stat.like_count

    for post_id, values in data.items():
        if values['view_count'] < values['like_count']:
            values['view_count'] += values['like_count'] + random.randint(50, 200)

    return data


def get_post_id_from_question_id(question_id):
    post = Post.query.with_entities('id').filter(Post.question==question_id).first()
    if post:
        return post.id
    else:
        return None



def get_answer_count(user_id):
    return Post.query.filter(Post.answer_author==user_id, Post.deleted==False).count()

def get_invite_count(invitable_id):
    return Invite.query.filter(Invite.invitable == invitable_id).count()


def has_invited(cur_user_id, invitable_id):
    return bool(Invite.query.filter(Invite.user==cur_user_id, Invite.invitable==invitable_id).limit(1).count())

def get_user_like_count(user_id):
    result = db.session.execute(text("""SELECT COUNT(post_likes.id) FROM post_likes
                                        WHERE post_likes.post 
                                        IN (SELECT posts.id from posts 
                                            WHERE posts.answer_author=:user_id) 
                                            AND post_likes.unliked=false;"""),
                                params={'user_id':user_id})
    count = 0
    for row in result:
        count = row[0]
    return count

def is_following(user_id, current_user_id):
    return bool(Follow.query.filter(Follow.user==current_user_id, Follow.followed==user_id, Follow.unfollowed==False).limit(1).count())

def is_follower(user_id, current_user_id):
    return bool(Follow.query.filter(Follow.user==user_id, Follow.followed==current_user_id, Follow.unfollowed==False).limit(1).count())

def is_liked(post_id, user_id):
    return bool(Like.query.filter(Like.post==post_id, Like.user==user_id, Like.unliked==False).count())

def get_post_reshare_count(post_id):
    return bool(Reshare.query.filter(Reshare.post==post_id).count())

def is_reshared(post_id, user_id):
    return bool(Reshare.query.filter(Reshare.post==post_id, Reshare.user==user_id).count())

def get_question_upvote_count(question_id):
    from math import sqrt, log
    from datetime import datetime, timedelta
    d = datetime.now() - timedelta(minutes = 5)
    question = Question.query.filter(Question.id == question_id).first()
    t = question.timestamp
    time_factor = 0
    if t:
        time_factor = int(time.mktime(t.timetuple())) % 7
    count_to_pump = Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False, Upvote.timestamp <= d).count() 
    count_as_such = Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False, Upvote.timestamp > d).count() 
    if count_to_pump:
        count = int(11*count_to_pump+ log(count_to_pump, 2) + sqrt(count_to_pump)) + count_as_such
        count += time_factor
    else:
        count = count_to_pump + count_as_such
    inflated_stat = InflatedStat.query.filter(InflatedStat.question==question_id).first()
    if inflated_stat:
        count += inflated_stat.upvote_count
    return count

def is_upvoted(question_id, user_id):
    return bool(Upvote.query.filter(Upvote.question==question_id, Upvote.user==user_id, Upvote.downvoted==False).count())

def get_upvoters(question_id, count=4):
    upvotes = Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False).order_by(Upvote.timestamp.desc()).limit(count)
    return [upvote.user for upvote in upvotes]

def has_enabled_anonymous_question(user_id):
    return bool(User.query.filter(User.id==user_id, User.allow_anonymous_question==True).count())

def user_is_celeb(user_id):
    return bool(User.query.filter(User.id==user_id, User.user_type==2).count())

def user_is_inactive(user_id):
    return bool(User.query.filter(User.id==user_id, User.monkness==-2).count())

def get_user_status(user_id):
    result = db.session.execute(text("""SELECT allow_anonymous_question, monkness, user_type 
                                        FROM users 
                                        WHERE id=:user_id LIMIT 1"""),
                                    params={'user_id':user_id}
                            )
    row = result.fetchone()
    return {'allow_anonymous_question':bool(row[0]), 'monkness':row[1], 'user_type':row[2]}


def get_video_states(video_urls={}):
    result = {}
    videos = Video.query.filter(Video.url.in_(video_urls.keys())).all()
    for video in videos:
        result[video.url] = {}
        result[video.url]['original'] = video.url
        result[video.url]['thumb'] = video.thumbnail
        if video.ultralow:
            result[video.url][0] = video.ultralow
        if video.low:
            result[video.url][200] = video.low
        if video.medium:
            result[video.url][400] = video.medium
        if video.opt:
            result[video.url][900] = video.opt
        if video.promo:
            result[video.url]['promo'] = video.promo

    for video_url, thumbnail_url in video_urls.items():
        video_obj = result.get(video_url)
        if not video_obj:
            result[video_url] = {'original':video_url, 'thumb':thumbnail_url}
    for key, value in result.items():
        for bitrate, url in value.items():
            #result[key][bitrate]=url.replace('https://s3.amazonaws.com/franklymestorage/', 'http://d35wlof4jnjr70.cloudfront.net/')
            #if bitrate is not 'thumb':
            #   result[key][bitrate] = 'http://api.frankly.me/videoview?url={vid_url}'.format(vid_url=result[key][bitrate])
            pass
    return result


def get_thumb_users(user_ids, cur_user_id=None):
    data = {}
    if user_ids:
        result = db.session.execute(text("""SELECT users.id, users.username, users.first_name, users.profile_picture, users.deleted,
                                                users.lat, users.lon, users.location_name, users.country_name, users.country_code,
                                                users.gender, users.bio, users.allow_anonymous_question, users.user_type, users.user_title,
                                                (SELECT count(user_follows.user) FROM user_follows 
                                                        WHERE user_follows.user=:cur_user_id
                                                                AND user_follows.followed=users.id
                                                                AND user_follows.unfollowed=False
                                                                ) as is_following
                                            FROM users 
                                            WHERE users.id in :user_ids"""),
                                        params={'user_ids':list(user_ids), 'cur_user_id':cur_user_id})
        for row in result:
            if not row[5] or not row[6]:
                coordinate_point = None
            else:
                coordinate_point = [row[5],row[6]]

            data.update({
                            row[0]:{
                                    'id':row[0],
                                    'username':row[1],
                                    'first_name':row[2],
                                    'profile_picture':row[3],
                                    'deleted':row[4],
                                    'location':{
                                                'coordinate_point':{'coordinates':coordinate_point},
                                                'location_name':row[7],
                                                'country_name':row[8],
                                                'country_code':row[9]
                                                },
                                    'gender':row[10],
                                    'bio':row[11],
                                    'allow_anonymous_question':bool(row[12]),
                                    'user_type':row[13],
                                    'user_title':row[14],
                                    'is_following':bool(row[15]),
                                    'channel_id':'user_{user_id}'.format(user_id=row[0])
                                    }
                        })
    return data

def get_questions(question_ids, cur_user_id=None):
    data = {}
    if question_ids:
        result = db.session.execute(text("""SELECT questions.id, questions.body,
                                                   questions.is_anonymous, questions.timestamp, questions.slug,
                                                   (SELECT count(question_upvotes.user) FROM question_upvotes
                                                    WHERE question_upvotes.question=questions.id 
                                                            AND question_upvotes.user=:cur_user_id
                                                            AND question_upvotes.downvoted=False) as is_upvoted
                                            FROM questions
                                            WHERE id in :question_ids"""),
                                        params={'question_ids':list(question_ids), 'cur_user_id':cur_user_id})
        for row in result:
            data.update({
                            row[0]:{'id':row[0],
                                    'body':row[1],
                                    'is_anonymous':row[2],
                                    'timestamp':row[3],
                                    'slug':row[4],
                                    'is_upvoted':bool(row[5])
                                    }
                        })
    return data
                                    


def user_view_profile(current_user_id, user_id, username=None):
    try:
        user = None
        if username:
            user = User.query.filter(User.username==username).one()
        elif user_id:
            user = User.query.get(user_id)

        if user and user.id == current_user_id:
            return {'user': user_to_dict(user)}

        if not user:
            raise NoResultFound()

        if current_user_id:
            if has_blocked(current_user_id, user.id):
                raise CustomExceptions.BlockedUserException()
        
        return {'user': guest_user_to_dict(user, current_user_id)}
    
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException('No user with this username/userid found')


def user_update_profile_form(user_id, first_name=None, bio=None, profile_picture=None, 
                            profile_video=None, user_type=None, phone_num=None, admin_upload=False,
                            user_title=None, email=None, moderated_by=None):
    update_dict = {}

    #user = User.objects.only('id').get(id=user_id)
    '''
    result = db.session.execute(text("""SELECT username, first_name, bio, profile_picture, cover_picture, profile_video from access_tokens 
                                        where id=:user_id LIMIT 1"""), params={'user_id':user_id})
    row = result.fetchone()
    '''
    
    user = User.query.get(user_id)
    
    existing_values = {'username': user.username,
                        'first_name':user.first_name,
                        'bio':user.bio,
                        'profile_picture':user.profile_picture,
                        'cover_picture':user.cover_picture,
                        'profile_video':user.profile_video,
                        'user_title':user.user_title
                        }

    if first_name:
        update_dict.update({'first_name':first_name})

    if bio:
        bio = bio.replace('\n', ' ').strip()
        bio = bio[:200]
        update_dict.update({'bio':bio})

    if profile_video:
        try:
            profile_video_url, cover_picture_url = media_uploader.upload_user_video(user_id=user_id, video_file=profile_video, video_type='profile_video')
            update_dict.update({'profile_video':profile_video_url, 'cover_picture':cover_picture_url})
        except IOError:
            raise CustomExceptions.BadRequestException('Couldnt read video file.')

    if profile_picture:
        tmp_path = '/tmp/request/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
        profile_picture.save(tmp_path)
        profile_picture_url = media_uploader.upload_user_image(user_id=user_id, image_file_path=tmp_path, image_type='profile_picture')
        update_dict.update({'profile_picture':profile_picture_url})
        try:
            os.remove(tmp_path)
        except:
            pass

    if admin_upload:
        if email:
            if email_available(email):
                update_dict.update({'email':email})
            else:
                raise CustomExceptions.UserAlreadyExistsException('Email is unavailable')
        if user_type!=None:
            update_dict.update({'user_type':user_type})

        if user_title:
            update_dict.update({'user_title':user_title})

    if not update_dict:
        raise CustomExceptions.BadRequestException('Nothing to update')
    
    user_archive =  UserArchive(user=user_id,
                                username=update_dict.get('username') or existing_values['username'],
                                first_name=update_dict.get('first_name') or existing_values['first_name'],
                                profile_picture=update_dict.get('profile_picture') or existing_values['profile_picture'],
                                cover_picture=update_dict.get('cover_picture') or existing_values['cover_picture'],
                                profile_video=update_dict.get('profile_video') or existing_values['profile_video'],
                                bio=update_dict.get('bio') or existing_values.get('bio'),
                                user_title=update_dict.get('user_title') or existing_values.get('user_title'),
                                moderated_by=moderated_by
                                )

    db.session.add(user_archive)
    User.query.filter(User.id==user_id).update(update_dict)
    
    

    if profile_video:
        add_video_to_db(video_url=profile_video_url,
                        thumbnail_url=cover_picture_url,
                        video_type='profile_video',
                        object_id=user_id,
                        username=user.username)
        
        async_encoder.encode_video_task.delay(profile_video_url, username=user.username)
    db.session.commit()
    return user_to_dict(user)


def user_follow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot follow yourself")

    if user_id!=cur_user_id:
        db.session.execute(text("""INSERT INTO user_follows (user, followed, unfollowed, timestamp) 
                                VALUES(:cur_user_id, :user_id, false, :timestamp) 
                                ON DUPLICATE KEY 
                                UPDATE unfollowed = false, timestamp=:timestamp"""),
                        params={'cur_user_id':cur_user_id, 'user_id':user_id, 'timestamp':datetime.datetime.now()}
                    )


    db.session.commit()
    notification_decision.decide_follow_milestone(user_id=user_id)
    return {'user_id': user_id}


def user_unfollow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot unfollow yourself")
    Follow.query.filter(Follow.user==cur_user_id, Follow.followed==user_id).update({'unfollowed':True})
    db.session.commit()
    return {'user_id': user_id}

def user_followers(cur_user_id, user_id, username=None, offset=0, limit=10):
    try:
        if username:
            user_id = User.query.with_entities(User.id).filter(User.username==username).one().id

        followers = User.query.with_entities(User.id, User.username, User.first_name, User.user_type, User.user_title
                                ).join( (Follow, Follow.followed==User.id)
                                ).filter(Follow.user==user_id, Follow.unfollowed==False
                                ).order_by(Follow.timestamp.desc()
                                ).offset(offset
                                ).limit(limit
                                ).all()

        followers_dict = []
        for follower in followers:
            
            are_you_following = is_following(user_id, cur_user_id) if cur_user_id else False
            is_he_follower = True if user_id==cur_user_id else is_follower(user_id, cur_user_id) if cur_user_id else False
            
            followers_dict.append({
                                'user_id':follower.id,
                                'username':follower.username,
                                'first_name':follower.first_name,
                                'last_name':None,
                                'user_title':follower.user_title,
                                'user_type':follower.user_type,
                                'is_following':are_you_following,
                                'is_follower':is_he_follower
                })

        next_index = offset+limit
        if len(followers_dict)<limit:
            next_index = -1

        return {'followers':followers_dict, 'next_index':next_index, 'offset':offset, 'limit':limit}
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException('No user found with that username')


def user_block(cur_user_id, user_id):
    if cur_user_id == user_id:
        return {'user_id': str(cur_user_id)}
    db.session.execute(text("""UPDATE user_follows 
                                SET user_follows.unfollowed=true
                                WHERE (user_follows.user=:user_id 
                                AND user_follows.followed=:cur_user_id)
                                OR (user_follows.user=:cur_user_id 
                                    AND user_follows.followed=:user_id)"""),
                        params={'user_id':user_id, 'cur_user_id':user_id})

    db.session.execute(text(""" INSERT INTO user_blocks (user, blocked_user, unblocked)
                                VALUES(:cur_user_id, :user_id, false)
                                ON DUPLICATE KEY 
                                UPDATE unblocked = false"""),
                        params={'cur_user_id':cur_user_id, 'user_id':user_id}
                        )
    db.session.commit()
    return {'user_id': user_id}

def user_unblock(cur_user_id, user_id):
    if cur_user_id == user_id:
        return {'user_id': str(cur_user_id)}
    Block.query.filter(Block.user==cur_user_id, Block.blocked_user==user_id).update({'unblocked':True})
    return {'user_id': user_id}

def user_block_list(user_id):
    result = db.session.execute(text("""SELECT id, username, first_name, profile_picture, deleted, gender, bio, allow_anonymous_question, user_title 
                                        FROM users 
                                        WHERE id IN (SELECT blocked_user 
                                                    FROM user_blocks 
                                                    WHERE user=:user_id)"""),
                                params={'user_id':user_id})

    blocked_users = [User(id=row[0], username=row[1], first_name=row[2], 
                            profile_picture=row[3], deleted=row[4], 
                            gender=row[5], bio=row[6], allow_anonymous_question=row[7], 
                            user_title=row[8]) for row in result]
    blocked_list = [thumb_user_to_dict(u) for u in blocked_users]

    return {'users': blocked_list}

def user_change_username(user_id, new_username):
    user = User.query.filter(User.id==user_id).one()
    
    if user.username.lower() == new_username.lower():
        User.query.filter(User.id==user_id).update({'username':new_username})
        db.session.commit()
        return {'username':new_username, 'status':'success', 'id':str(user_id)}
    
    elif username_available(new_username):
        User.query.filter(User.id==user_id).update({'username':new_username})
        db.session.commit()
        async_encoder.encode_video_task.delay(user.profile_video, username=new_username, profiles=['promo'], redo=True)
        return {'username':new_username, 'status':'success', 'id':str(user_id)}
    else:
        raise CustomExceptions.UnameUnavailableException('Username invalid or not available')

def user_change_password(user_id, new_password):
    if password_is_valid(new_password):
        User.query.filter(User.id==user_id).update({'password':new_password})
        db.session.commit()
        return {'status':'success', 'id':user_id}
    else:
        raise CustomExceptions.UnameUnavailableException('Password is invalid')


def user_exists(username=None, email=None, phone_number=None):
    if username:
        return {'exists': not username_available(username), 'username':username}
    elif email:
        return {'exists': not email_available(email), 'email':email}
    else:
        raise CustomExceptions.BadRequestException()


def user_get_settings(user_id):
    result = db.session.execute(text("""SELECT allow_anonymous_question, notify_like, notify_follow, notify_question, 
                                            notify_comments, notify_mention, notify_answer, timezone 
                                        FROM users 
                                        WHERE id=:user_id 
                                        LIMIT 1"""),
                                params={'user_id':user_id})
    row = result.fetchone()
    if row:
        return {"allow_anonymous_question":row[0],
                "notify_like":row[1],
                "notify_follow":row[2],
                "notify_question":row[3],
                "notify_comments":row[4],
                "notify_mention":row[5],
                "notify_answer":row[6],
                "timezone":row[7]
                }

def user_update_settings(user_id, allow_anonymous_question, notify_like, notify_follow, 
                        notify_question, notify_comments, notify_mention, notify_answer, timezone):
    User.query.filter(User.id==user_id).update({
                                                'allow_anonymous_question':allow_anonymous_question,
                                                'notify_like':notify_like,
                                                'notify_follow':notify_follow,
                                                'notify_question':notify_question,
                                                'notify_comments':notify_comments,
                                                'notify_mention':notify_mention,
                                                'notify_answer':notify_answer,
                                                'timezone':timezone
                                                })
    return True


def user_update_location(user_id, lat, lon, country=None, country_code=None, loc_name=None):
    if lat == 0.0 and lon == 0.0:
        return
   
    if loc_name and country_code:
        User.query.filter(User.id==user_id).update({   "lat":lat,
                                                        "lon":lon,
                                                        "location_name":loc_name,
                                                        "country_code":country_code,
                                                        "country_name":country
                                                    })

    else:
        User.query.filter(User.id==user_id).update({   "lat":lat,
                                                        "lon":lon,
                                                    })
    '''
    Post.query.filter(Post.answer_author==user_id, 
                        or_(Post.lat==None, (Post.lat==0.0, Post.lon==0.0))
                        ).update({  "lat":lat,
                                    "lon":lon,
                                    "location_name":loc_name,
                                    "country_code":country_code,
                                    "country_name":country
                                })
    '''


def update_push_id(cur_user_id, device_id, push_id):
    AccessToken.query.filter(AccessToken.user==cur_user_id,
                             AccessToken.device_id==device_id
                             ).update({'push_id':push_id})


def user_update_access_token(user_id, acc_type, token, secret=None):
    try:
        if acc_type=='facebook':
            user_data = get_data_from_external_access_token('facebook', token, external_token_secret=None)
            User.query.filter(User.id==user_id, User.facebook_id==user_data['social_id']).update({'facebook_token':token, 'facebook_write_permission':True})

        if acc_type=='twitter':
            if not secret:
                raise CustomExceptions.BadRequestException('Missing access secret')
            user_data = get_data_from_external_access_token('twitter', token, external_token_secret=secret)
            User.query.filter(User.id==user_id, User.facebook_id==user_data['social_id']).update({'twitter_token':token, 'twitter_write_permission':True})
        
        return {'success':True}
    
    except CustomExceptions.InvalidTokenException:
        raise CustomExceptions.BadRequestException('invalid token')


def make_question_slug(body, question_id):
    import slugify
    stop_words = ["in", "it", "its", "is", "it's", "on", "so", "to", 
                    "were", "are", "was", "at", "in", "so", "be"]
    body = sanitize_question_body(body)
    if len(body)>150:
        for word in stop_words:
            body = body.replace(' '+word+' ', ' ')
    if len(body)>150:
        body = body[:150]
    sentence = "{body} {question_id}".format(body=body, question_id=question_id)
    slug = slugify.slugify(unicode(sentence))
    return slug

    
def sanitize_question_body(body):
    if len(body)>200:
        body = body.replace('\n', ' ').replace('  ', ' ').strip()
    return body

def question_is_clean(body):
    special_chars = flag_words.SPECIAL_CHARS_AND_NUMBERS
    bad_words = flag_words.BAD_WORDS
    for special_char in special_chars:
        body = body.replace(special_char, '')
    word_list = body.split()
    print word_list
    for word in word_list:
        if word.lower() in bad_words:
            return False
    return True


def question_ask(cur_user_id, question_to, body, lat, lon, is_anonymous, from_widget, added_by=None):

    if has_blocked(cur_user_id, question_to):
        raise CustomExceptions.BlockedUserException()

    user_status = get_user_status(question_to)

    if not cur_user_id == question_to and is_anonymous and not user_status['allow_anonymous_question']:
        raise CustomExceptions.NoPermissionException('Anonymous question not allowed for the user')

    public = True if user_status['user_type']==2 else False #if user is celeb

    question_id = get_item_id()

    short_id = get_new_short_id(for_object='question')
    slug = make_question_slug(body, short_id)
    clean = question_is_clean(body)


    question = Question(question_author=cur_user_id, question_to=question_to,
                body=body.capitalize().replace('\n', ' ').strip(), is_anonymous=is_anonymous, public=public,
                lat=lat, lon=lon, slug=slug, short_id=short_id,
                id = question_id, added_by=added_by, flag=int(clean))

    db.session.add(question)

    db.session.commit()

    if question_to != cur_user_id and clean:
        notification.ask_question(question_id=question.id)
        make_email.question_asked(question_from=cur_user_id, question_to=question_to, question_id=question.id,
                                  question_body = question.body,
                                  from_widget=from_widget)

    resp = {'success':True, 'id':str(question.id), 'question':question_to_dict(question)}
    return resp


def question_list(user_id, offset, limit, version_code=0):

    questions_query = Question.query.filter(Question.question_to==user_id, 
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.flag.in_([1, 2])
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(func.count(Upvote.id).desc()
    #                                        ).order_by(Question.score.desc()
                                            ).offset(offset)
    
    questions = questions_to_dict(questions_query.limit(limit))
    questions = [{'question':q, 'type':'question'} for q in questions]

    next_index = str(offset+limit) if questions else "-1"
    if version_code>51:
        next_index = offset+limit if questions else -1
    return {'questions': questions, 'count': len(questions),  'next_index' : next_index}


def question_list_public(current_user_id, user_id, username=None, offset=0, limit=10, version_code=0):
    if offset<0:
        return {'current_user_questions':[], 'questions': [], 'count': 0,  'next_index' : -1}


    if username:
        try:
            user_id = User.query.with_entities('id', 'username').filter(User.username==username).one().id
        except NoResultFound:
            raise CustomExceptions.UserNotFoundException('User Not Found')
            
    if current_user_id and has_blocked(current_user_id, user_id):
        raise CustomExceptions.BlockedUserException('User Not Found')

    cur_user_questions = []

    if offset == 0 and current_user_id:
        cur_user_questions = Question.query.filter(Question.question_to==user_id,
                                                    Question.question_author==current_user_id,
                                                    Question.deleted==False,
                                                    Question.is_answered==False,
                                                    Question.is_ignored==False,
                                                    Question.flag.in_([1, 2])
                                                    #Question.public==True
                                                    ).order_by(Question.timestamp.desc()
                                                    ).offset(0).limit(5).all()

    cur_user_question_ids = [q.id for q in cur_user_questions]
    
    questions_query = Question.query.filter(~Question.id.in_(cur_user_question_ids),
                                            Question.question_to==user_id, 
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            #Question.public==True
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(Question.score.desc()
                                            ).order_by(func.count(Upvote.id).desc()
                                            ).offset(offset)

    question_objects = questions_query.limit(limit).all()

    questions = questions_to_dict(cur_user_questions+question_objects, current_user_id)
    
    cur_user_questions = questions[0:len(cur_user_questions)]
    cur_user_questions = [{'question':q, 'type':'question'} for q in cur_user_questions]

    other_questions = questions[len(cur_user_questions):]
    other_questions.sort(key=lambda q: q['ask_count']*q['score'], reverse=True)
    questions = [{'question':q, 'type':'question'} for q in other_questions]

    next_index = str(offset+limit) if questions else "-1"
    if version_code>51:
        next_index = offset+limit if questions else -1

    return {'current_user_questions':cur_user_questions, 'questions': questions, 'count': len(questions),  'next_index' : next_index}


def question_upvote(cur_user_id, question_id):
    if Question.query.filter(
                            Question.id==question_id, 
                            #Question.public==True, 
                            Question.question_to!=cur_user_id,
                            Question.deleted==False,
                            Question.is_ignored==False,
                            Question.is_answered==False
                            ).count():
        db.session.execute(text("""INSERT INTO question_upvotes (user, question, downvoted, timestamp) 
                                    VALUES(:cur_user_id, :question_id, false, :timestamp) 
                                    ON DUPLICATE KEY 
                                    UPDATE downvoted = false, timestamp=:timestamp"""),
                            params={'cur_user_id':cur_user_id,
                                    'question_id':question_id,
                                    'timestamp':datetime.datetime.now()}
                            )
        db.session.commit()
        notification_decision.push_question_notification(question_id=question_id)
    else:
        raise CustomExceptions.BadRequestException("Question is not available for upvote")
    
    return {'id': question_id, 'success': True}

def question_downvote(cur_user_id, question_id):
    if Question.query.filter(Question.id==question_id, Question.question_author==cur_user_id).count():
        raise CustomExceptions.BadRequestException("You cannot downvote your own question")
    result = Upvote.query.filter(Upvote.user==cur_user_id, Upvote.question==question_id).update({'downvoted':True})
    db.session.commit()
    return {'id':question_id, 'success':bool(result)}


def question_ignore(user_id, question_id):
    result = Question.query.filter(  Question.id==question_id,
                            Question.question_to==user_id,
                            Question.is_answered==False,
                            Question.deleted==False
                        ).update({'is_ignored':True})
    db.session.commit()
    return {"question_id":question_id, "success":bool(result)}


def post_reshare(cur_user_id, post_id):
    reshare = Reshare(post=post_id, user=cur_user_id)
    db.session.add(reshare)
    db.session.commit()
    return {'success':True}


def post_reshare_delete(cur_user_id, post_id):
    Reshare.query.filter(Reshare.post==post_id, Reshare.user==cur_user_id).delete()
    db.session.commit()
    return {'success':True}


def post_like(cur_user_id, post_id):
    result = db.session.execute(text("""SELECT answer_author, question_author
                                        FROM posts
                                        WHERE id=:post_id AND deleted=false
                                        LIMIT 1"""),
                                params={'post_id':post_id}
                        )
    row = result.fetchone()
    if not row:
        raise CustomExceptions.PostNotFoundException('Post not available for action')
    
    answer_author, question_author= row

    if not (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
        db.session.execute(text("""INSERT INTO post_likes (user, post, unliked, timestamp) 
                                    VALUES(:cur_user_id, :post_id, false, :timestamp) 
                                    ON DUPLICATE KEY 
                                    UPDATE unliked = false, timestamp=:timestamp"""),
                            params={'cur_user_id':cur_user_id, 'post_id':post_id,
                                    'timestamp':datetime.datetime.now()}
                            )

        db.session.commit()

        notification_decision.decide_post_milestone(post_id=post_id, user_id=answer_author)
        return {'id': post_id, 'success':True}

    else:
        raise CustomExceptions.PostNotFoundException('Post not available for action')

def post_unlike(cur_user_id, post_id):
    result = Like.query.filter(Like.user==cur_user_id, Like.post==post_id).update({'unliked':True})
    db.session.commit()
    return {'id':post_id, 'success':bool(result)}

def post_delete(cur_user_id, post_id):
    result = Post.query.filter(Post.id==post_id, Post.answer_author==cur_user_id, Post.deleted==False).update({'deleted':True})
    db.session.commit()
    return {'id':post_id, 'success':bool(result)}

def post_view(cur_user_id, post_id, client_id=None):
    try:
        post_pending = False
        if client_id:
            pending_post_data = get_pending_post(client_id)
            if pending_post_data:
                post_pending = True
                question = Question.query.get(pending_post_data['question_id'])
            else:
                post = Post.query.filter(Post.client_id==client_id, Post.deleted==False).one()
        
        else:
            post = Post.query.filter(Post.id==post_id, Post.deleted==False).one()

        if cur_user_id and (has_blocked(cur_user_id, post.answer_author) or has_blocked(cur_user_id, post.question_author)):
            raise CustomExceptions.BlockedUserException()
        
        if post_pending:
            return {'question':question_to_dict(question, cur_user_id), 'pending':post_pending}

        return {'post': post_to_dict(post, cur_user_id), 'pending':post_pending}
    except NoResultFound:
        raise CustomExceptions.PostNotFoundException("The post does not exist or has been deleted")


def question_view(current_user_id, question_id, short_id):
    try:
        if short_id:
            question = Question.query.filter(Question.short_id==short_id, 
                                            Question.deleted==False,
                                            Question.is_ignored==False,
                    #this condition is to   #or_(Question.is_answered==True,
                    #have private questions #    Question.public==True,
                                            #    Question.question_to==current_user_id)
                                            ).one()
        else:
            question = Question.query.filter(Question.id==question_id, 
                                            Question.deleted==False,
                                            Question.is_ignored==False,
                    #this condition is to   #or_(Question.is_answered==True,
                    #have private questions #    Question.public==True,
                                            #    Question.question_to==current_user_id)
                                            ).one()

        question_to = User.query.filter(User.id==question.question_to).one()

        if question.flag == 0 and question.question_author!=current_user_id:
            raise CustomExceptions.ObjectNotFoundException('The question does not exist or has been deleted.')
        if question.is_answered:
            post = Post.query.filter(Post.question==question.id, Post.deleted==False).one()
            return {'is_answered':question.is_answered, 'post':post_to_dict(post, current_user_id), 'question':question_to_dict(question, current_user_id)}
        
        return {'is_answered':question.is_answered, 'question':question_to_dict(question, current_user_id)}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('The question does not exist or has been deleted.')


def comment_add(cur_user_id, post_id, body, lat, lon):
    result = db.session.execute(text("""SELECT answer_author, question_author
                                        FROM posts
                                        WHERE id=:post_id AND deleted=false 
                                        LIMIT 1"""),
                                params={'post_id':post_id}
                                )
    row = result.fetchone()
    if not row:
        raise CustomExceptions.PostNotFoundException('Post not available for action')
    
    answer_author, question_author= row

    if not (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
        from database import get_item_id
        comment = Comment(id=get_item_id(), on_post=post_id, body=body, comment_author=cur_user_id,
                          lat=lat, lon=lon, timestamp=datetime.datetime.now())
        db.session.add(comment)

        db.session.commit()

        notification.comment_on_post(comment_id=comment.id, comment_author=cur_user_id, post_id=post_id)


        return {'comment': comment_to_dict(comment), 'id':comment.id, 'success':True}
    else:
        CustomExceptions.PostNotFoundException('Post not available for action')


def comment_delete(cur_user_id, comment_id):
    try:      
        comment = Comment.query.filter(Comment.id==comment_id, Comment.deleted==False).one()
        if not comment:
            raise CustomExceptions.ObjectNotFoundException('Comment Not available for action')
        
        if comment.comment_author==cur_user_id or Post.query.filter(Post.id==comment.on_post, Post.answer_author==cur_user_id, Post.deleted==False).count():
            Comment.query.filter(Comment.id==comment_id, 
                                    Comment.deleted==False,
                                    Comment.comment_author==cur_user_id
                                    ).update({'deleted':False})
            db.session.commit()
            return {'success': True}
        else:
            raise CustomExceptions.ObjectNotFoundException('Comment Not available for action')
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('Comment Not available for action')

def get_comments_for_posts(cur_user_id, post_ids, offset=0, limit=3):
    single_query = """SELECT * FROM (SELECT comments.id, comments.body, comments.on_post, comments.comment_author, comments.timestamp 
                                        FROM comments
                                        WHERE comments.on_post=:post_id_{idx}
                                            AND comments.comment_author NOT IN (SELECT user_blocks.blocked_user FROM user_blocks WHERE user_blocks.user=:cur_user_id AND user_blocks.unblocked=false)
                                            AND comments.deleted=false
                                        ORDER BY comments.timestamp DESC
                                        LIMIT :offset,:limit
                                    ) alias_{idx}

                    """
    params = {'cur_user_id':cur_user_id, 'offset':offset, 'limit':limit}
    idx = 0
    queries = []
    response = {}
    for post_id in post_ids:
        queries.append(single_query.format(idx=idx))
        params.update({'post_id_{idx}'.format(idx=idx):post_id})
        idx +=1
        response[post_id] = {'comments':[], 'post': post_id, 'next_index':offset+limit}

    all_comments = []
    if queries:
        query = ' UNION ALL '.join(queries)
        result = db.session.execute(text(query), params=params)
        all_comments = [row for row in result]

    all_comments_dict = comments_to_dict(all_comments)
    
    for comment in all_comments_dict:
        response[comment['on_post']]['comments'].append(comment)

    return response



def comment_list(cur_user_id, post_id, offset, limit):
        result = db.session.execute(text("""SELECT answer_author, question_author
                                            FROM posts
                                            WHERE id=:post_id AND deleted=false 
                                            LIMIT 1"""),
                                    params={'post_id':post_id}
                                    )
        row = result.fetchone()
        if cur_user_id:
            if not row:
                raise CustomExceptions.PostNotFoundException("Comments for this post is not available")
            answer_author, question_author= row
            
            if (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
                raise CustomExceptions.BlockedUserException("Comments for this post is not available")

            blocks = Block.query.filter(or_(Block.user==cur_user_id, Block.blocked_user==cur_user_id)).all()
            blocked_users = set()
            for block in blocks:
                if block.user == cur_user_id:
                    blocked_users.add(block.blocked_user)
                else:
                    blocked_users.add(block.user)
            comments = Comment.query.filter(Comment.on_post==post_id, Comment.deleted==False
                                        ).filter(~Comment.comment_author.in_(blocked_users)
                                        ).order_by(Comment.timestamp.desc()
                                        ).offset(offset
                                        ).limit(limit).all()
        else:
            comments = Comment.query.filter(Comment.on_post==post_id, Comment.deleted==False
                                        ).order_by(Comment.timestamp.desc()
                                        ).offset(offset
                                        ).limit(limit).all()
        comments = comments_to_dict(comments)
        next_index = offset+limit if comments else -1
        return {'comments': comments, 'post': post_id, 'next_index':next_index}


def get_user_timeline(cur_user_id, user_id, offset, limit, include_reshares=False, device_id=False):
    
    if cur_user_id and has_blocked(cur_user_id, user_id):
        raise CustomExceptions.UserNotFoundException('User does not exist')
    
    if include_reshares:    
        posts_query = Post.query.filter(or_(Post.answer_author==user_id,
                                            Post.id.in_(Reshare.query.filter(Reshare.user==user_id))
                                            ), Post.deleted==False
                                        ).join(Reshare
                                        ).order_by(Reshare.timestamp.desc()
                                        ).order_by(Post.timestamp.desc())

    else:
        posts_query = Post.query.filter(Post.answer_author==user_id, Post.deleted==False).order_by(Post.timestamp.desc())

    total_count = posts_query.count()
    if offset == -1:
        return {'stream': [], 'count':0, 'next_index':-1, 'total':total_count}
    data = []
    if total_count<1 and device_id=='web':
        data = question_list_public(cur_user_id, user_id, username=None, offset=offset, limit=limit, version_code=0)['questions']
    else:
        question_data = []
        if device_id=='web':
            question_data = question_list_public(cur_user_id, user_id, username=None, offset=offset, limit=2, version_code=0)['questions']
        
        posts = posts_query.offset(offset).limit(limit-len(question_data)).all()
        posts = posts_to_dict(posts, cur_user_id)
        data  = [{'type':'post', 'post':post} for post in posts]
        for item in question_data:
            idx = random.randint(0, len(data))
            data.insert(idx, item)

    next_index = offset+limit if data else -1
    
    return {'stream': data, 'count':len(data), 'next_index':next_index, 'total':total_count}
    

def get_celeb_users_for_feed(offset, limit, cur_user_id=None, users=[], feed_type='home', visit=0):
    #for home feed only users will be included
    #for discover feed users will be excluded
    user_day = visit/2
    if cur_user_id:
        result = db.session.execute(text('SELECT user_since from users where id=:user_id'),
                                                    params={'user_id':cur_user_id})
        for row in result:
            user_since = max(datetime.datetime(2014, 12, 28, 18, 32, 35, 270652), row[0])
            user_time_diff = datetime.datetime.now()-user_since
            user_day = user_time_diff.days

    if feed_type=='home':
        celeb_user_query = User.query.join(UserFeed).filter(User.id.in_(users))
    else:
        celeb_user_query = User.query.join(UserFeed).filter(~User.id.in_(users))

    celeb_user_query = celeb_user_query.filter( User.deleted==False,
                                                User.user_type==2,
                                                User.profile_video!=None,
                                                UserFeed.day<=user_day,
                                                UserFeed.day!=-1
                                            ).order_by(UserFeed.day.desc()
                                            ).order_by(UserFeed.score
                                            ).offset(offset
                                            ).limit(limit)
    return celeb_user_query.all()

def home_feed(cur_user_id, offset, limit, web):
    from manage_feed import get_home_feed

    if offset == -1:
        return {
                'stream' : [],
                'count' : 0,
                'next_index' : -1
            }

    feeds, next_index = get_home_feed(cur_user_id, offset, limit)

    return {'stream': feeds, 'count':len(feeds), 'next_index':next_index}



def discover_posts(cur_user_id, offset, limit, web, lat=None, lon=None, visit=0):
    followings = Follow.query.filter(Follow.user==cur_user_id, Follow.unfollowed==False)
    followings = [follow.followed for follow in followings]
    followings = filter(lambda x:x,map(lambda x:x if x not in config.TEST_USERS else None, followings))

    posts = Post.query.filter(~Post.answer_author.in_(followings+[cur_user_id])
                    ).filter(Post.deleted==False, Post.popular==True
                    ).order_by(Post.timestamp.desc()
                    ).offset(offset
                    ).limit(limit
                    ).all()

    posts = posts_to_dict(posts, cur_user_id)
    feeds = [{'type':'post', 'post':post} for post in posts]
    next_index = offset+limit if posts else -1
    
    skip = offset/5
    celeb_limit = 2
    
    if offset != 0:
        skip = skip+celeb_limit
    
    users_to_ignore = []
    if cur_user_id:
        users_to_ignore.append(cur_user_id)
    celeb_users = get_celeb_users_for_feed(skip, celeb_limit, cur_user_id=cur_user_id, users=users_to_ignore, feed_type='discover', visit=visit)
    
    last_extra_feed_position = 0
    for user in celeb_users:
        questions_feed = []
        if web:
            questions_query = Question.query.filter(Question.question_to==user.id, 
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.public==True
                                            )
            count = questions_query.filter(Question.score>300).count()
            if count:
                questions_query = questions_query.filter(Question.score>300)
            else:
                count = questions_query.count()
            
            max_limit = count-2 if count>2 else count
            question_offset = random.randint(0, max_limit)
            
            questions = questions_query.order_by(Question.score.desc()
                                        ).offset(question_offset
                                        ).limit(2)
            questions_feed = []
            if web:
                questions_feed = [{'type':'question', 'questions':question_to_dict(q, cur_user_id)} for q in questions.all()]
                
            elif questions.count()==2:
                questions_feed = [{'type':'questions', 'questions':make_celeb_questions_dict(user, questions.all(), cur_user_id)}]
        
        extra_feed = [{'type':'user', 'user':guest_user_to_dict(user, cur_user_id)}]
        random_index = last_extra_feed_position + 2
        count = 0
        for item in extra_feed:
            feeds.insert(random_index, item)
            random_index +=1
            count +=1
        last_extra_feed_position = random_index+count
    
    next_index = offset+limit if feeds else -1


    return {'stream': feeds, 'count':len(feeds), 'next_index':next_index}


def create_forgot_password_token(username=None, email=None):
    from mail import make_email
    try:
        import hashlib
        if username:
            user = User.query.filter(User.username==username).one()
        elif email:
            user = User.query.filter(User.email==email).one()
        else:
            raise CustomExceptions.BadRequestException('Either Username or Email must be provided')

        forgot_password_query = ForgotPasswordToken.query.filter(ForgotPasswordToken.user==user.id,
                                            ForgotPasswordToken.used_at == None,
                                            ForgotPasswordToken.valid==True,
                                            ForgotPasswordToken.created_at>datetime.datetime.now()-datetime.timedelta(days=1))
        if forgot_password_query.count()>3:
            return {'success':False}
        
        token_salt = 'ANDjdnbsjKDND=skjkhd94bwi20284HFJ22u84'
        token_string = '%s+%s+%s'%(str(user.id), token_salt, time.time())
        token = hashlib.sha256(token_string).hexdigest()
        now_time = datetime.datetime.now()

        forgot_token = ForgotPasswordToken(user=user.id, token=token, email=user.email)
        db.session.add(forgot_token)
        make_email.forgot_password(user.email, token=token, receiver_name=user.first_name, user_id=user.id)
        db.session.commit()

        return {'success':True}
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException('Username or email does not exist.')


def forgot_password_token_is_valid(token, return_object=False):
    token_object = ForgotPasswordToken.query.filter(ForgotPasswordToken.token==token,
                                            ForgotPasswordToken.used_at == None,
                                            ForgotPasswordToken.valid==True).first()
    if token_object:
        timediff = datetime.datetime.now() - token_object.created_at
        if timediff.total_seconds()>3600*48:
            ForgotPasswordToken.query.filter(ForgotPasswordToken.token==token).update({'valid':False})
            db.session.commit()
            token = None
    if return_object:
        return token_object
    return bool(token_object)


def check_forgot_password_token(token):
    token_object = forgot_password_token_is_valid(token, return_object=True)
    if token_object:
        user = User.query.get(token_object.user)
        return {'valid':True, 'token':token, 'user':thumb_user_to_dict(user)}
    raise CustomExceptions.BadRequestException('Token Not valid')
    #return {'valid':False, 'token':token, 'user':None}



def reset_password(token, password):
    if not password_is_valid(password):
        raise CustomExceptions.PasswordTooShortException('Password is not valid')
    
    token_object = forgot_password_token_is_valid(token, return_object=True)
    if not token_object:
        raise CustomExceptions.ObjectNotFoundException('Invalid token')

    user = User.query.filter(User.id == token_object.user).one()
    user_change_password(user_id=user.id, new_password=password)
    
    #mark token as used and invalid
    ForgotPasswordToken.query.filter(ForgotPasswordToken.token==token_object.token).update({'used_at':datetime.datetime.now(),
                                                                                            'valid':False})
    db.session.commit()

    return {'success':True,
            'error':None, 
            'message':'Your password has been reset'}


def install_ref(device_id, url):
    #url = "https://play.google.com/store/apps/details?id=me.frankly&referrer=utm_source%3Dsource%26utm_medium%3Dmedium%26utm_term%3Dterm%26utm_content%3Dcontent%26utm_campaign%3Dname"
    from urllib import unquote
    ref_string = None
    try:
        ref_string = unquote(url)
    except:
        pass
    device_type = 'android' if len(device_id)<=16 else 'ios'
    i = Install(device_id=device_id, url=url, device_type=device_type, ref_data=ref_string)
    db.session.add(i)
    db.session.commit()


def get_new_short_id(for_object):
    id_chars = []
    for i in range(6):
        id_chars.append(random.choice(config.ALLOWED_CHARACTERS))
    cid = 's%s'%(''.join(id_chars))
    
    if for_object == 'post':
        already_exists = Post.query.filter(Post.client_id==cid).count()
    elif for_object == 'question':
        already_exists = Question.query.filter(Question.short_id==cid).count()
    
    if not already_exists:
        return cid
    return get_new_short_id(for_object)


def set_pending_post(cur_user_id, question_id, client_id):
    redis_pending_post.setex(client_id, cur_user_id+'_'+question_id, 3600*24)
    return {'success':True, 'client_id':client_id}

def get_pending_post(client_id):
    pending_post = redis_pending_post.get(client_id)
    if pending_post:
        try:
            answer_author_id, question_id = pending_post.split('_')
            return {'answer_author_id':answer_author_id, 'question_id':question_id}
        except:
            pass
    return None


def add_video_post(cur_user_id, question_id, video, answer_type,
                        lat=None, lon=None, client_id=None,
                        show_after = None):
    try:
        if cur_user_id in config.ADMIN_USERS:
            question = Question.query.filter(Question.id==question_id,
                                            Question.is_ignored==False,
                                            Question.deleted==False).one()
            answer_author = question.question_to
        else:
            answer_author = cur_user_id
            question = Question.query.filter(Question.question_to==cur_user_id,
                                            Question.id==question_id,
                                            Question.is_ignored==False,
                                            Question.deleted==False).one()

        if question.is_answered:
            post = Post.query.filter(Post.question==question.id, Post.answer_author==answer_author).one()
        
        else:
            if has_blocked(answer_author, question.question_author):
                raise CustomExceptions.BlockedUserException("Question not available for action")
            try:
                video_url, thumbnail_url = media_uploader.upload_user_video(user_id=cur_user_id, video_file=video, video_type='answer')
            except IOError:
                raise CustomExceptions.BadRequestException('Couldnt read video file.')
            curuser = User.query.filter(User.id == cur_user_id).one()


            if not client_id:
                client_id = question.short_id
                
            post = Post(question=question_id,
                        question_author=question.question_author, 
                        answer_author=answer_author,                    
                        answer_type=answer_type,
                        media_url=video_url,
                        thumbnail_url=thumbnail_url,
                        client_id=client_id,
                        lat=lat,
                        lon=lon,
                        id = get_item_id())
            if show_after and type(show_after) == int:
                post.show_after = show_after
            
            db.session.add(post)

            Question.query.filter(Question.id==question_id).update({'is_answered':True})

            add_video_to_db(video_url=video_url,
                            thumbnail_url=thumbnail_url,
                            video_type='answer_video',
                            object_id=post.id,
                            username=curuser.username)
            async_encoder.encode_video_task.delay(video_url, username=curuser.username)


            db.session.commit()
            redis_pending_post.delete(client_id)
            notification.new_post(post_id=post.id, question_body=question.body)


        return {'success': True, 'id': str(post.id), 'post':post_to_dict(post, cur_user_id)}

    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException("Question not available for action")

def update_required(device_type, version_code):
    should_update = False
    if device_type == 'ios':
        should_update = version_code < config.CURRENT_IOS_VERSION_CODE    
    if device_type == 'android':
        should_update = version_code < config.CURRENT_ANDROID_VERSION_CODE

    return should_update


def get_notifications(cur_user_id, device_id, version_code, notification_category, offset, limit):
    original_limit = limit

    # Setting the seen on notifications
    # only if it is the first fetch
    if offset == 0:
        db.session.execute(text("Update user_notifications set seen_at = :current_time where user_id = :user_id ; "),
                           params = {'user_id': cur_user_id,
                                     'current_time':datetime.datetime.now(),
                                    })
        db.session.commit()



    device_type = get_device_type(device_id)
    
    if device_type == 'ios':
        app_store_link = config.IOS_APPSTORE_DEEPLINK
    
    if device_type == 'android':
        app_store_link = config.ANDROID_APPSTORE_LINK

    

    notifications = []
    update = check_app_version_code(device_type, version_code)
    if update['hard_update'] or update['soft_update']:

        update_notification = {
                                    "user_to" : cur_user_id,
                                    "type" : 1,
                                    "id" : 'update_required_ios',
                                    "text" : "A new version of Frankly.me is available. Click here to update.",
                                    "styled_text":"A new version of Frankly.me is available. Click here to update.",
                                    "icon_url" : "https://d30y9cdsu7xlg0.cloudfront.net/png/68793-84.png",
                                    "group_id": 'update_required',
                                    "link" : app_store_link,
                                    "deeplink" : app_store_link,
                                    "timestamp" : int(time.mktime(datetime.datetime.now().timetuple())),
                                    "seen" : False
                                }
        notifications.append(update_notification)
        limit -= 1    

    results = db.session.execute(text("""SELECT notifications.id, notifications.text, 
                                                notifications.icon, notifications.type,
                                                notifications.object_id, notifications.link,
                                                user_notifications.added_at, user_notifications.seen_at
                                            FROM notifications JOIN user_notifications
                                                ON notifications.id = user_notifications.notification_id
                                            WHERE user_notifications.user_id = :cur_user_id
                                                AND user_notifications.list_type = :list_type
                                                AND user_notifications.show_on in :device_type
                                            GROUP BY notifications.type, notifications.object_id
                                            ORDER BY user_notifications.added_at DESC
                                            LIMIT :offset,:limit
                                        """),
                                    params = {'cur_user_id':cur_user_id,
                                                'list_type':notification_category,
                                                'limit':limit,
                                                'offset':offset,
                                                'device_type':['all']
                                            }
                                    )
    
    from collections import defaultdict
    icon_object_ids = defaultdict(list)
    icons = {}
    
    for row in results:
        notification = {
                        "user_to" : cur_user_id,
                        "type" : 1,
                        "id" : row[0],
                        "text" : row[1].replace('<b>', '').replace('</b>', ''),
                        "styled_text":row[1],
                        "icon_url" : row[2],
                        "group_id": '-'.join([str(row[3]),str(row[4])]),
                        "link" : row[5],
                        "deeplink" : row[5],
                        "timestamp" : int(time.mktime(row[6].timetuple())),
                        "updated_at":int(time.mktime(row[6].timetuple())),
                        "seen" : bool(row[7])
                        }
        notifications.append(notification)

    count = len(notifications)
    next_index = -1 if count<original_limit else offset+limit

    return {'notifications':notifications, 'count':count, 'next_index':next_index, 'current_time':int(time.mktime(datetime.datetime.now().timetuple()))}


def get_notification_count(cur_user_id, device_id, version_code):

    count = 0
    device_type = get_device_type(device_id)
    update = check_app_version_code(device_type, version_code)
    if update['hard_update'] or update['soft_update']:
        count += 1

    last_fetch_time = datetime.datetime.now() - datetime.timedelta(days=100)
    last_fetch_time_query = ''
    results = db.session.execute(text("""SELECT user_notification_info.last_notification_fetch_time
                                        FROM user_notification_info
                                        WHERE user_id = :cur_user_id
                                        ORDER BY user_notification_info.last_notification_fetch_time
                                        LIMIT 0,1
                                    """), params={'cur_user_id':cur_user_id}
                                )
    for row in results:
        last_fetch_time = row[0]

    results = db.session.execute(text("""SELECT count(*)
                                        FROM notifications JOIN user_notifications
                                            ON notifications.id = user_notifications.notification_id
                                        WHERE user_notifications.user_id = :cur_user_id
                                            AND user_notifications.seen_at is null
                                            AND user_notifications.added_at > :last_fetch_time
                                    """),
                                params={'cur_user_id':cur_user_id,
                                          'last_fetch_time':last_fetch_time
                                        }
                                )
    for row in results:
        count += row[0]
    return count


def push_notification_seen(push_notification_id):
    from models import UserPushNotification

    UserPushNotification.query.filter(UserPushNotification.id == push_notification_id).update(
        {'clicked_at':datetime.datetime.now()})


    db.session.commit()




def logout(access_token, device_id):
    from app import redis_client
    device_type = get_device_type(device_id)
    if device_type=='web':
        redis_client.delete(device_id)
        return True
    count = AccessToken.query.filter(AccessToken.access_token==access_token, AccessToken.device_id==device_id).update({'active':False})
    return bool(count)


def get_question_authors_image(question_id):
    from image_processors import make_collage
    
    upvoters = get_upvoters(question_id, count=10)

    result = db.session.execute(text("""SELECT profile_picture 
                                        FROM users
                                        WHERE id in (SELECT question_author
                                                    FROM questions
                                                    WHERE id=:question_id)"""),
                                params={'question_id':question_id})
    question_author_image = None
    for row in result:
        question_author_image = row[0]
    
    upvoters_image = []
    if upvoters:
        result = db.session.execute(text("""SELECT profile_picture
                                            FROM users
                                            WHERE id in :user_ids"""),
                                params={'user_ids':upvoters})
    
        for row in result:
            upvoters_image.append(row[0])

    all_image_urls = [item for item in [question_author_image]+upvoters_image if item]

    path = make_collage(all_image_urls[:8])
    
    f = open(path)
    return f

def interview_media_controller(offset, limit):
    media = Video.query.filter().offset(offset).limit(limit).all()
    res = {'data' : []}
    if len(media):
        for obj in media:
            media_obj = media_dict(obj.url, obj.thumbnail)
            res['data'].append(media_obj)
        if len(media) < limit:
            res['next_offset'] = -1
        else:
            res['next_offset'] = offset + limit
        res['count'] = len(media)
    else:
        res['count'] = 0
        res['next_offset'] = -1
    return res



def web_hiring_form(name, email, phone_num, role):

    import gdata.spreadsheet.service
    import gdata.docs
    import gdata.docs.service
    import gdata.spreadsheet.service
    import datetime
    import pytz

    login_email = config.SPREADSHEET_EMAIL
    login_password = config.SPREADSHEET_PASSWORD

    spreadsheet_key = '1ZPZL_GFY6G8ARuvtrnpv8bM2IKs8WK61x21c5jb4I98'
    # All spreadsheets have worksheets. I think worksheet #1 by default always
    # has a value of 'od6'
    worksheet_id = 'od6'

    spr_client = gdata.spreadsheet.service.SpreadsheetsService()
    spr_client.debug = True
    spr_client.email = login_email
    spr_client.password = login_password
    spr_client.source = 'Frankly Hiring Form'
    spr_client.ProgrammaticLogin()


    cur_datetime = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    cur_datetime = cur_datetime.strftime('%d/%m/%Y %H:%M:%S')

    row_data = {
                'name': name,
                'email': email,
                'phone': phone_num,
                'role': role,
                'submitted': cur_datetime
        }

    spr_client.InsertRow(row_data, spreadsheet_key, worksheet_id)
    return {'success':True}


def view_video(url, count=1):
    return
    url = url.replace('http://d35wlof4jnjr70.cloudfront.net/', 'https://s3.amazonaws.com/franklymestorage/')
    redis_views.incr(url, count)

def query_search(cur_user_id, query, offset, limit, version_code=None):
    results = []
    if 'test' in query:
        return {
                "q": query,
                "count": 0,
                "results": [ ],
                "next_index": -1
            } 
    if version_code and int(version_code) > 42 and offset == 0:
        search_filter_invitable = or_( Invitable.name.like('{query}%'.format(query = query)),
                                   Invitable.name.like('% {query}%'.format(query = query))
                                )
        invitable = Invitable.query.filter(search_filter_invitable).limit(1).all()
        if invitable:
            results.append({'type':'invitable', 'invitable' : invitable_to_dict(invitable[0], cur_user_id)})
            limit = limit - 1
    '''
    if offset == 0 and ('trending' in query.lower() or 'new on' in query.lower()):
        search_default = SearchDefault.query.filter(SearchDefault.category == query).order_by(SearchDefault.score).all()
        for s in search_default:
            results.append({'type':'user', 'user':thumb_user_to_dict(User.query.filter(User.id == s.user).first(), cur_user_id)})
    '''
    
    import search
    response = search.search(cur_user_id, query.lower(), offset, limit)
    response['results'] = results + response['results']
    response['q'] = query
    return response


def return_none_feed():
    return {
            'next_index' : -1,
            'count' : 0,
            'stream' : []
        }

def prompt_for_profile_video(user_id):
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=48)
    if user_id == '481bc87c43bc4812b0e333ecd9cd4c2c':
        return True
    return bool(User.query.filter(User.id==user_id, User.user_since<time_threshold, User.profile_video==None).count())


def user_profile_request(current_user_id, request_for, request_type):

    request_id = get_item_id()
    result = db.session.execute(text('''
                                        INSERT INTO profile_requests
                                        (id, request_for, request_by, request_type, created_at)
                                        VALUES
                                        (:id, :request_for, :request_by, :request_type, :created_at)
                                        ON DUPLICATE KEY
                                        UPDATE request_count = request_count + 1, updated_at=:updated_at
                                     '''),
                                params={
                                    'id': request_id,
                                    'request_for': request_for,
                                    'request_by': current_user_id,
                                    'request_type': request_type,
                                    'created_at': datetime.datetime.now(),
                                    'updated_at': datetime.datetime.now()
                                })
    db.session.commit()

   
    notification.user_profile_request(user_id=current_user_id, request_for=request_for,
                                      request_type=request_type,
                                      request_id=request_id)

    return {'success': True}


def get_new_discover(current_user_id, offset, limit, device_id, version_code, visit=0, append_top=''):
    from manage_discover import get_discover_list
    append_top_usernames = [username.strip().lower() for username in append_top.split(',')]
    users = User.query.filter(User.username.in_(append_top_usernames)).all()
    
    resp = [{'type':'user', 'user':guest_user_to_dict(current_user_id, u)} for u in users]
    
    add_profile_video_prompt = False

    if offset ==0 and current_user_id:
        add_profile_video_prompt = prompt_for_profile_video(current_user_id)
        limit -= 1
    
    day_count = 0
    if get_device_type(device_id)=='web':
        day_count = visit/3600*24
    
    resp.extend(get_discover_list(current_user_id, offset, limit, 
                                    day_count=day_count, add_super=True, 
                                    exclude_users=[u.id for u in users]))
    if add_profile_video_prompt:
        resp.insert(3, {'type':'upload_profile_video', 'upload_profile_video':{}})

    
    next_index = offset+limit if len(resp) else -1
    
    return {
            'next_index' : next_index,
            'count' : len(resp),
            'stream' : resp
           }

def discover_post_in_cqm(cur_user_id, offset, limit, device_id, version_code, web = None, lat = None, lon = None, visit = None, append_top=''):
    from models import CentralQueueMobile, User, Question, Post
    
    device_type = get_device_type(device_id)

    if offset == -1:
        return return_none_feed()

    user_time_diff = 1
    
    feeds_count = 0
    requested_limit = limit
    if cur_user_id:
        result = db.session.execute(text('SELECT timestampdiff(minute,user_since,now()) from users where id=:user_id'),
                                        params={'user_id':cur_user_id})
        for row in result:
            user_time_diff = int(row[0]) + 1
    elif visit:
        user_time_diff = int(visit/60)
        
    response = []
    append_top_usernames = []
    if offset ==0: 
        if cur_user_id and prompt_for_profile_video(cur_user_id) and (device_type!='android' or version_code>46):
            response.append({'type':'upload_profile_video', 'upload_profile_video':{}})
            limit -= 1
            

        append_top_usernames = [item.strip().lower() for item in append_top.split(',') if item.strip()]
        append_top_users = User.query.filter(User.username.in_(append_top_usernames), User.profile_video!=None).all()
        append_top_users.sort(key=lambda u:append_top_usernames.index(u.username.lower()))
        limit -= len(append_top_users)
        requested_limit = limit

        response.extend([{'type':'user', 'user': guest_user_to_dict(user, cur_user_id)} for user in append_top_users])
   
    item_count = CentralQueueMobile.query.count()
    count_arr = IntervalCountMap.query.filter(IntervalCountMap.minutes <= user_time_diff).all()
    feeds_count = sum(map(lambda x:x.count, count_arr))
    if feeds_count > item_count:
        feeds_count = item_count
    if offset > feeds_count:
        return return_none_feed()

    temp_offset = feeds_count - offset
    if limit > temp_offset:
        limit = temp_offset
    temp_offset = temp_offset - limit

    feeds = CentralQueueMobile.query.order_by(CentralQueueMobile.score.asc()).offset(temp_offset).limit(limit).all()
    users_in_feeds = filter(lambda x:x, map(lambda x:x.user, feeds))
    
    filter_these_from_feeds = []
    if cur_user_id and users_in_feeds:
        filter_these_from_feeds = db.session.execute(text('SELECT followed FROM user_follows WHERE user = :cur_user_id and \
                                                        followed in :users_in_feeds and unfollowed=false'),
                                                        params = {'cur_user_id':cur_user_id,
                                                                  'users_in_feeds':users_in_feeds})
    filter_these_from_feeds = [x[0] for x in filter_these_from_feeds]

    results = []
    for obj in feeds:
        if obj.user:
            if obj.user in filter_these_from_feeds: continue
            user = User.query.filter(User.id == obj.user, User.profile_video != None, ~User.username.in_(append_top_usernames)).first() 
            if user:
                results.append({'type':'user', 'user': guest_user_to_dict(user, cur_user_id)})
                if web:
                    questions_query = Question.query.filter(Question.question_to==obj.user, 
                                                    Question.deleted==False,
                                                    Question.is_answered==False,
                                                    Question.is_ignored==False,
                                                    Question.public==True
                                                    )
                    questions = questions_query.order_by(Question.score.desc()
                                                ).limit(3)
                    questions_feed = [{'type':'questions', 'questions':question_to_dict(q, cur_user_id)} for q in questions.all()]
                    results.extend(questions_feed)
        elif obj.question:
            results.append({'type':'questions', 'questions': question_to_dict(Question.query.filter(Question.id == obj.question).first(), cur_user_id)})
        else:
            results.append({'type':'post', 'post' : post_to_dict(Post.query.filter(Post.id == obj.post).first(), cur_user_id)})

    results.reverse()
    response.extend(results)
    next_index = offset + limit if len(feeds) >= requested_limit else -1
    
    return {
            'next_index' : next_index,
            'count' : len(response),
            'stream' : response
           }

                                                  
def get_is_following(cur_user_id, user_ids):
    results = db.session.execute(text("""SELECT user_follows.followed
                                        FROM user_follows
                                        WHERE user_follows.user = :user_id
                                        AND user_follows.followed IN :user_ids
                                        AND user_follows.unfollowed = false
                                      """),
                                        params={'user_id': cur_user_id, 'user_ids': user_ids}
                                )

    followed = [row[0] for row in results]
    followed_ids = {id:id in followed for id in user_ids}  
    return followed_ids                                               



def search_default(cur_user_id=None):
    from collections import defaultdict
    resp = redis_client.get('search_default')
    resp = 0
    if resp:
        resp = json.loads(resp)
    else:
        # categories_order = ["Trending Now", "Actors", "Singers", "Twitter Celebrities", "Radio Jockeys", "Subject Experts", "New on Frankly", "Authors", "Entrepreneurs", "Chefs", "Politicians", "Comedians", "Bands"]
        categories = SearchCategory.query.filter().order_by(SearchCategory.score.desc()).all()
        categories_order = [cat.name for cat in categories]
        results = db.session.execute(
            text(
                """ SELECT 
                        sc.name, u.id, u.username, u.first_name,
                        u.user_type, u.user_title, u.profile_picture,
                        u.bio, u.gender, sd.show_always
                    FROM 
                        users u JOIN search_defaults sd ON u.id=sd.user
                        JOIN search_categories sc ON sd.category=sc.id
                    ORDER BY 
                        sd.score
                """
            )
        )
        category_results = defaultdict(list)
        for row in results:
            user_dict = {
                'id':row[1],
                'username':row[2],
                'first_name':row[3],
                'last_name':None,
                'user_type':row[4],
                'user_title':row[5],
                'profile_picture':row[6],
                'bio':row[7],
                'gender':row[8],
                'is_following':False,
                'channel_id':'user_{user_id}'.format(user_id=row[1]),
                'show_always': bool(row[9])
            }
            category_results[row[0]].append(user_dict)

        for category, users in category_results.items():
            if len(category_results[category]) > 3:
                show_always_users = filter(lambda x: x['show_always'], users)
                show_always_count = len(show_always_users)
                if show_always_count < 3:
                    random_users = [user for user in users if user not in show_always_users]
                    random_count = 3 - show_always_count
                    category_results[category] = random.sample(show_always_users, show_always_count)
                    category_results[category].extend(random.sample(random_users, random_count))
                else: 
                    category_results[category] = random.sample(show_always_users, 3)

        resp = []
        for cat in categories_order:
            if category_results.get(cat):
                resp.append({'category_name':cat, 'users':category_results[cat]})
        redis_client.setex('search_default', json.dumps(resp), 600)

    if cur_user_id:
        user_ids = []
        for result in resp:
            for user in result['users']:
                user_ids.append(user['id'])
        followed_ids = get_is_following(cur_user_id, user_ids)
        for result in resp:
            for user in result['users']:
                user['is_following'] = followed_ids[user['id']]

    return {'results':resp}

def invite_celeb(cur_user_id, invitable_id):
    try:
        i = Invite(cur_user_id, invitable_id)
        db.session.add(i)
        db.session.commit()
        return {'success':True}
    except Exception as e:
        print e
        return {'success':False}

def user_follows_list(cur_user_id, count):
    follow_object_list = Follow.query.filter(Follow.user==str(cur_user_id)).limit(count).all()
    user_id_list = []
    for follow_object in follow_object_list:
        user_id_list.append(follow_object.followed)
    return user_id_list

def random_celebrity_list(count):
    offst = random.randint(0, 100)
    celebrity_object_list = User.query.filter(User.user_type==2).offset(offst).limit(count)
    random_celeb_list = []
    for celebrity_object in celebrity_object_list:
        random_celeb_list.append(celebrity_object.id)
    return random_celeb_list


def top_liked_users(cur_user_id, count=5):
    if count > 20:
        count = 20
    liked_users_list = most_liked_users(current_user_id=str(cur_user_id))
    liked_user_ids = []
    for i in xrange(len(liked_users_list)):
        liked_user_ids.append(liked_users_list[i][0])
    if len(liked_user_ids) < count:
        liked_user_ids.extend(user_follows_list(cur_user_id, count))
    if len(liked_user_ids) < count:
        liked_user_ids.extend(random_celebrity_list(count))

    return {'users': get_thumb_users(liked_user_ids[:count]).values()}

def save_feedback_response(cur_user_id, medium, message, version):
    from models import Feedback
    feedback = Feedback(user=str(cur_user_id), medium=medium, message=message, version=version)
    db.session.add(feedback)
    db.session.commit()
    return {'success': True}

def update_post_share(current_user_id, post_id, platform):
    from models import PostShare
    post_share = PostShare(user=current_user_id, post=post_id, platform=platform)
    db.session.add(post_share)
    db.session.commit()
    return {'success':True, 'id':post_id}


def parse_channel_id(channel_id):
    channel_data = channel_id.split('_')
    channel_type = channel_data[0]
    channel_id = '_'.join(channel_data[1:])

    return channel_type, channel_id


def get_channel_feed(cur_user_id, channel_id, offset, limit, device_id=None, version_code=None, append_top='', visit=0):
    channel_type, channel_id = parse_channel_id(channel_id)
    
    device_type = get_device_type(device_id) if device_id else None
    web = True if device_type == 'web' else False

    if channel_type == 'user':
        response = get_user_timeline(cur_user_id, channel_id, offset, limit)
        response['header'] = user_view_profile(cur_user_id, channel_id)
        response['header'].update({'type':'user'})
        return response

    if channel_type == 'feed':
        return home_feed(cur_user_id, offset, limit, web)

    if channel_type == 'discover':
        return get_new_discover(cur_user_id, offset, limit, device_id, version_code, append_top=append_top, visit=visit)

def get_channel_list(cur_user_id, device_id, version_code):
    feed_banner = {'type':'banner',
                    'bg_image':None,
                    'icon':None,
                    'name':'Feed',
                    'channel_id':'feed',
                    'description':None}
    discover_banner = {'type':'banner',
                        'bg_image':None,
                        'name':'Discover',
                        'icon':None,
                        'channel_id':'discover',
                        'description':None
                        }

    search_fragment = {'type':'search',
                        'bg_image':None,
                        'views':[]
                        }
    
    search_default_results = search_default(cur_user_id=cur_user_id)['results']

    for item in search_default_results:
        search_icons = {'type':'icon_list',
                        'name':item['category_name'],
                        'icons':[]
                        }

        for user in item['users']:
            search_icons['icons'].append({'type':'icon_user', 'user':user})
        
        search_fragment['views'].append(search_icons)
    return {'channel_list':[feed_banner, discover_banner, search_fragment]}


def get_item_from_slug(current_user_id, username, slug):
    try:
        question = Question.query.filter(Question.slug==slug, 
                                            Question.deleted==False,
                                            Question.is_ignored==False,
                                            or_(Question.is_answered==True,
                                                Question.public==True,
                                                Question.question_to==current_user_id)
                                            ).one()
        question_to = User.query.filter(User.id==question.question_to).one()
        if question_to.username.lower() != username.lower():
            
            return {'redirect':True, 'username':question_to.username, 'slug':question.slug}
        
        if question.is_answered:
            post = Post.query.filter(Post.question==question.id, Post.deleted==False).one()
            return {'redirect':False, 'is_answered':question.is_answered, 'post':post_to_dict(post, current_user_id)}
        
        return {'redirect':False, 'is_answered':question.is_answered, 'question':question_to_dict(question, current_user_id)}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('The question does not exist or has been deleted.')


def check_app_version_code(device_type,device_version_code):
    hard_update = False
    soft_update= False
    if device_type == 'android':
        hard_update = device_version_code < config.ANDROID_NECESSARY_VERSION_CODE
        soft_update = device_version_code < config.ANDROID_LATEST_VERSION_CODE

    elif device_type == 'ios':
        hard_update = device_version_code < config.IOS_NECESSARY_VERSION_CODE
        soft_update = device_version_code < config.IOS_LATEST_VERSION_CODE

    return {'hard_update':hard_update, 'soft_update':soft_update}


def check_app_version_code(device_type,device_version_code):
    hard_update_resp = {'hard_update':True,'soft_update':False}
    soft_update_resp = {'hard_update':False,'soft_update':True}
    no_update_resp = {'hard_update':False,'soft_update':False}
    
    if device_type == 'android':
        if device_version_code < config.ANDROID_NECESSARY_VERSION_CODE :
            resp = hard_update_resp
        elif device_version_code < config.ANDROID_LATEST_VERSION_CODE :
            resp = soft_update_resp
        else:
            resp = no_update_resp  
    elif device_type == 'ios':
        if device_version_code < config.IOS_NECESSARY_VERSION_CODE :
            resp = hard_update_resp
        elif device_version_code < config.IOS_LATEST_VERSION_CODE :
            resp = soft_update_resp
        else:
            resp = no_update_resp
    return resp


def report_abuse(current_user_id, object_type, object_id, reason):
    report_abuse = ReportAbuse(user_by=current_user_id, entity_type=object_type, entity_id=object_id, reason=reason)
    db.session.add(report_abuse)
    db.session.commit()
    return {'success':True, 'object_type':object_type, 'object_id':object_id}

def get_rss():
    import rss_manager
    rss_manager.generate_answers_rss()
    with open('/tmp/franklymeanswers.xml','r') as f:
        s = f.read()
    return s

def contact_file_upload(current_user_id, uploaded_file, device_id):
    contacts = uploaded_file.read()
    return user_upload_contacts(current_user_id, device_id, contacts)


def user_upload_contacts(user_id, device_id, contacts):
    from AES_Encryption import decryption
    contacts_json = json.loads(decryption(contacts))
    empty_contacts_filter = lambda contact: contact['email'] or contact['number']
    contacts = filter(empty_contacts_filter, contacts_json['contacts'])
    return contacts

    for item in contacts:
        for number in item['number']:
            number = number.replace(' ', '').replace('-', '').replace('.', '')
            contact_object = Contact(contact=number, contact_type='phone_number', contact_name=item['name'], user=user_id)
            db.session.add(contact_object)
            try:
                db.session.commit()
            except Exception as e:
                print e

        for email in item['email']:
            email = email.strip()
            contact_object = Contact(contact=email, contact_type='phone_email', contact_name=item['name'], user=user_id)
            db.session.add(contact_object)
            try:
                db.session.commit()
            except Exception as e:
                print e
    
    return {'success':True}

def add_contact(name, email, organisation, message, phone):
    from base64 import b64encode as enc

    b64msg = enc(name + email + organisation + message + phone)
    contact = ContactUs.query.filter(ContactUs.b64msg == b64msg).all()
    if contact:
        return {'success' : True}
    else:
        contact = ContactUs(name, email, organisation, message, phone, b64msg)
        db.session.add(contact)
        db.session.commit()
    return {'success' : True}


def get_resized_image(image_url, height=262, width=262):
    from image_processors import resize_video_thumb
    import os
    image_path = media_uploader.download_file(image_url)
    resized_image = resize_video_thumb(image_path, height, width)
    if os.path.exists(image_path):
        os.remove(image_path)
    return resized_image


def register_bad_email(email,reason_type,reason_subtype):
    new_bad_email = BadEmail(email,reason_type,reason_subtype)
    db.session.add(new_bad_email)
    try:
        db.session.commit() # TODO : handle duplicate insert in unique column
    except Exception as e: 
        db.session.rollback()
        print e.message
    return {'success':'true', 'email':email , 'reason':reason_type}


def list_name_available(name):
    if len(name)<2 or len(name)>30:
        return False
    for char in name:
        if char not in config.ALLOWED_CHARACTERS+['-']:
            return False
    return not bool(List.query.filter(List.name==name).count())


def list_display_name_available(name):
    if len(name)<2 or len(name)>40:
        return False
    return True


def lists_to_dict(lists, cur_user_id=None):
    if type(lists) != list:
        lists = [lists]
    list_dicts = []
    for l in lists:
        list_dict = {
                    'id'          :l.id,
                    'name'        :l.name,
                    'display_name':l.display_name,
                    'icon_image'  :l.icon_image,
                    'banner_image':l.banner_image,
                    'is_owner'    :l.owner==cur_user_id if cur_user_id else None,
                    'followable'  :l.followable,
                    'if_following':False,
                    'show_on_remote':l.show_on_remote
                    }
        list_dicts.append(list_dict)
    return list_dicts


def list_items_to_dict(list_items, cur_user_id=None):
    if type(list_items) != list:
        list_items = [list_items]
    list_item_dicts = []

    for item in list_items:
        if item.child_user_id:
            item = User.query.filter(User.id==item.child_user_id).first()
        else:
            item = List.query.filter(List.id==item.child_list_id).first()
        if type(item) == User:

            item_dict = {
                                'id'             : item.id,
                                'username'       : item.username,
                                'first_name'     : item.first_name,
                                'profile_picture': item.profile_picture,
                                'gender'         : item.gender,
                                'user_type'      : item.user_type,
                                'bio'            : item.bio,
                                'user_title'     : item.user_title,
                                'is_following'   : False
                            }
            item_dict = {'type':'user', 'user':item_dict} 
        
        elif type(item) == List:
            item_dict = lists_to_dict([item], cur_user_id)[0]
            item_dict = {'type':'list', 'list':item_dict} 
        list_item_dicts.append(item_dict)
    return list_item_dicts


def create_list(cur_user_id, name, display_name, icon_image=None, banner_image=None, owner=None, show_on_remote=False, score=0):
    if not list_name_available(name):
        raise CustomExceptions.UserAlreadyExistsException('That list name is already taken')
    if not list_display_name_available(name):
        raise CustomExceptions.UserAlreadyExistsException('That list display name is not valid')

    new_list = List(id=get_item_id(), name=name, display_name=display_name, created_by=cur_user_id, owner=owner or cur_user_id, show_on_remote=show_on_remote, score=score)
    db.session.add(new_list)
    db.session.commit()
    return {'success':True, 'list':lists_to_dict(new_list, cur_user_id)[0]}


def edit_list(cur_user_id, list_id, name=None, display_name=None, icon_image=None, banner_image=None, owner=None, show_on_remote=None, score=None):
    try:
        list_to_edit = List.query.filter(List.id==list_id, List.owner==cur_user_id, List.deleted==False).one()
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('Either the list is deleted or you dont have permission to edit it.')
    changed = False

    if name:
        if not list_name_available(name):
            raise CustomExceptions.UserAlreadyExistsException('That list name is already taken')
        list_to_edit.name = name
        changed = True

    if display_name:
        if not list_display_name_available(name):
            raise CustomExceptions.UserAlreadyExistsException('That list display name is not valid')
        list_to_edit.display_name = display_name
        changed = True

    if icon_image:
        tmp_path = '/tmp/request/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
        icon_image.save(tmp_path)
        icon_image_url = media_uploader.upload_user_image(user_id=user_id, image_file_path=tmp_path, image_type='list_icon_image')
        try:
            os.remove(tmp_path)
        except:
            pass
        list_to_edit.icon_image = icon_image_url
        changed = True

    if banner_image:
        tmp_path = '/tmp/request/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
        banner_image.save(tmp_path)
        banner_image_url = media_uploader.upload_user_image(user_id=user_id, image_file_path=tmp_path, image_type='list_banner_image')
        try:
            os.remove(tmp_path)
        except:
            pass
        list_to_edit.banner_image = banner_image_url
        changed = True

    if owner:
        list_to_edit.owner = owner

    if show_on_remote!=None:
        list_to_edit.show_on_remote = show_on_remote

    if score!=None:
        list_to_edit.score = score

    if changed:
        list_to_edit.updated_at = datetime.datetime.now()
        list_to_edit.updated_by = cur_user_id
        db.session.add(list_to_edit)
        db.session.commit()

    return {'success':True, 'list':lists_to_dict([list_to_edit], cur_user_id)[0]}


def delete_list(cur_user_id, list_id):
    success = List.query.filter(List.id==list_id, List.owner==cur_user_id).update({'deleted':True})
    db.session.commit()
    return {'success':True, 'list_id':list_id}


def add_child_to_list(cur_user_id, parent_list_id, child_user_id=None, child_list_id=None, show_on_list=False, score=0, featured=False):
    if (not child_user_id and not child_list_id) or (child_list_id and child_user_id):
        raise CustomExceptions.BadRequestException('Either child_user_id or child_list_id must be provided.')
    try:
        parent_list = List.query.filter(List.id==parent_list_id, List.owner==cur_user_id, List.deleted==False).one()
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('Either the list is deleted or you dont have permission to edit it.')
    if ListItem.query.filter(ListItem.parent_list_id==parent_list_id,
                            ListItem.child_list_id==child_list_id,
                            ListItem.child_user_id==child_user_id
                        ).first():
        raise CustomExceptions.BadRequestException('child_user_id or child_list_id is already a child of the parent list.')


    list_item = ListItem(parent_list_id=parent_list_id, created_by=cur_user_id, child_user_id=child_user_id,
                child_list_id=child_list_id, show_on_list=show_on_list, score=score, is_featured=featured)

    db.session.add(list_item)
    db.session.commit()
    return {'success':True, 'list_item':list_items_to_dict([list_item], cur_user_id)[0]}


def edit_list_child(cur_user_id, parent_list_id, child_user_id, child_list_id, show_on_list=None, score=None, deleted=False, featured=None):
    if (not child_user_id and not child_list_id) or (child_list_id and child_user_id):
        raise CustomExceptions.BadRequestException('Either child_user_id or child_list_id must be provided.')
    try:
        parent_list = List.query.filter(List.id==list_id, List.owner==cur_user_id, List.deleted==False).one()
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('Either the list is deleted or you dont have permission to edit it.')

    try:
        list_item = ListItem.query.filter(ListItem.parent_list_id==parent_list_id,
                            ListItem.child_list_id==child_list_id,
                            ListItem.child_user_id==child_user_id
                        ).one()
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('The given user_id or list_id is not a child of the parent list.')


    if show_on_list != None:
        list_item.show_on_list = show_on_list
    if score != None:
        list_item.score = score
    if deleted != None:
        list_item.deleted = deleted
    if featured != None:
        list_item.is_featured = is_featured

    db.session.add(list_item)
    db.session.commit()
    return {'success':True, 'list_item':list_items_to_dict(list_item, cur_user_id)[0]}

def get_list_from_name_or_id(list_id):
    if len(list_id)>30:
        list_object = List.query.filter(List.id==list_id, List.deleted==False).one()
    else:
        list_object = List.query.filter(List.name==list_id, List.deleted==False).one()
    return list_object


def get_list_items(cur_user_id, list_id, offset=0, limit=20):
    try:
        print list_id
        if not list_id:
            list_dicts = [{'type':'list', 'list':l} for l in lists_to_dict(get_top_level_lists(offset=offset, limit=limit), cur_user_id)]
        else:
            parent_list = get_list_from_name_or_id(list_id)

            list_items = ListItem.query.filter(ListItem.parent_list_id==parent_list.id,
                                                    ListItem.deleted==False,
                                                    ListItem.show_on_list==True
                                                ).order_by(ListItem.score
                                                ).offset(offset
                                                ).limit(limit
                                                ).all()
            print list_items
            list_dicts = list_items_to_dict(list_items, cur_user_id)
            print list_dicts

        count = len(list_dicts)
        next_index = -1 if count<limit else offset+limit

        return {'list_items':list_dicts, 
                'list_id':list_id,
                'count':count,
                'next_index':next_index}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('The list does not exist or has been deleted')


def get_top_level_lists(offset=0, limit=20):
    lists = List.query.filter(List.show_on_remote==True,
                                List.deleted==False
                            ).order_by(List.score
                            ).offset(offset
                            ).limit(limit
                            ).all()

    return lists


def get_remote(cur_user_id, offset=0, limit=20):
    remote = []
    if offset == 0:
        feed_banner = {'type':'banner',
                        'content_type':'channel',
                        'channel':{
                                    'bg_image':None,
                                    'icon':None,
                                    'name':'Feed',
                                    'channel_id':'feed',
                                    'description':None
                                    }
                        }
        discover_banner = {'type':'banner',
                            'content_type':'channel',
                            'channel':{
                                        'bg_image':None,
                                        'name':'Discover',
                                        'icon':None,
                                        'channel_id':'discover',
                                        'description':None
                                        }
                            }
        remote.extend([feed_banner, discover_banner])
        limit -=2

    list_dicts = lists_to_dict(get_top_level_lists(offset=offset, limit=limit), cur_user_id)
    remote.extend([{'type':'banner', 'content_type':'list', 'list':list_dict} for list_dict in list_dicts])

    count = len(remote)
    next_index = -1 if count<limit else offset+limit

    return {'count':count, 'next_index':next_index, 'stream':remote}

def get_list_user_ids(list_id):
    queries = """SELECT * FROM (SELECT list_items.child_user_id, list_items.parent_list_id, list_items.score
                                FROM list_items 
                                WHERE list_items.parent_list_id = :parent_list_id 
                                    AND list_items.deleted = False
                                    AND list_items.child_user_id is NOT null

                                UNION

                                SELECT list_items.child_user_id, list_items.parent_list_id, list_items.score
                                FROM list_items 
                                WHERE list_items.parent_list_id in (SELECT list_items.child_list_id 
                                                                    FROM list_items 
                                                                    WHERE list_items.parent_list_id = :parent_list_id 
                                                                        AND list_items.deleted = False
                                                                        AND list_items.child_list_id is NOT null
                                                                    )
                                    AND list_items.deleted = False
                                    AND list_items.child_user_id is NOT null
                                ) as result
            ORDER BY result.parent_list_id=:parent_list_id, result.score
        """
    results = db.session.execute(text(queries), params={'parent_list_id':list_id})
    
    user_ids = [row[0] for row in results]
    print user_ids
    return user_ids

    
def get_featured_users(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)
            users = User.query.join(ListItem, User.id==ListItem.child_user_id
                                    ).filter(ListItem.parent_list_id==parent_list.id,
                                                ListItem.deleted==False,
                                                ListItem.child_user_id!=None,
                                                ListItem.show_on_list==True,
                                                User.deleted==False
                                            ).order_by(ListItem.score
                                            ).offset(offset
                                            ).limit(limit
                                            ).all()
            print users
            print parent_list
        else:
            from models import DiscoverList
            users = User.query.join(DiscoverList, User.id==DiscoverList.user
                                ).order_by(DiscoverList.is_super.desc(), DiscoverList.id.desc()).offset(offset).limit(limit).all()
        print users
        user_dicts = guest_users_to_dict(users, cur_user_id)
        user_dicts = [{'type':'user', 'user':user_dict} for user_dict in user_dicts]
        
        count = len(user_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':user_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')



def get_trending_users(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)
        if list_id:
            user_ids = get_list_user_ids(parent_list.id)
            users = User.query.filter(User.id.in_(user_ids)).offset(offset).limit(limit).all()
        else:
            users = User.query.join(DiscoverList, User.id==DiscoverList.user
                                ).filter(User.deleted==False
                                ).order_by(User.id
                                ).offset(offset).limit(limit).all()

        user_dicts = guest_users_to_dict(users, cur_user_id)
        user_dicts = [{'type':'user', 'user':user_dict} for user_dict in user_dicts]
        
        count = len(user_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':user_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')



def get_featured_posts(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)
            posts = Post.query.filter(Post.deleted==False,
                                Post.answer_author.in_(get_list_user_ids(parent_list.id))
                                ).order_by(Post.id.desc()).offset(offset).limit(limit).all()
        else:
            posts = Post.query.join(DiscoverList, Post.id==DiscoverList.post
                                ).filter(Post.deleted==False
                                ).order_by(DiscoverList.id.desc()
                                ).offset(offset
                                ).limit(limit
                                ).all()


        post_dicts = posts_to_dict(posts, cur_user_id)
        post_dicts = [{'type':'post', 'post':post_dict} for post_dict in post_dicts]
        
        count = len(post_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':post_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')


def get_trending_posts(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)
            posts = Post.query.filter(Post.deleted==False,
                                Post.answer_author.in_(get_list_user_ids(parent_list.id))
                                ).order_by(Post.id).offset(offset).limit(limit).all()

        else:
            posts = Post.query.join(DiscoverList, Post.id==DiscoverList.post
                                ).filter(Post.deleted==False
                                ).order_by(Post.id.desc()
                                ).offset(offset
                                ).limit(limit
                                ).all()

        post_dicts = posts_to_dict(posts, cur_user_id)
        post_dicts = [{'type':'post', 'post':post_dict} for post_dict in post_dicts]
        
        count = len(post_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':post_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')


def get_featured_questions(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)
            questions = Question.query.filter(Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.flag.in_([1, 2]),
                                            Question.question_to.in_(get_list_user_ids(parent_list.id))
                                        ).order_by(Question.score.desc()
                                        ).offset(offset
                                        ).limit(limit
                                        ).all()
        else:
            questions = Question.query.filter(Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.flag.in_([1, 2]),
                                            Question.question_to.in_([item.user for item in DiscoverList.query.filter(DiscoverList.user!=None).all()])
                                        ).order_by(Question.score.desc()
                                        ).offset(offset
                                        ).limit(limit
                                        ).all()

        question_dicts = questions_to_dict(questions, cur_user_id)
        question_dicts = [{'type':'question', 'question':question_dict} for question_dict in question_dicts]
        
        count = len(question_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':question_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')


def get_trending_questions(cur_user_id, list_id, offset=0, limit=20):
    try:
        if list_id:
            parent_list = get_list_from_name_or_id(list_id)

            questions = Question.query.filter(Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.flag.in_([1, 2]),
                                            Question.question_to.in_(get_list_user_ids(parent_list.id))
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(func.count(Upvote.id).desc(), Question.score.desc()
                                            ).offset(offset
                                            ).limit(limit
                                            ).all()
        else:
            questions = Question.query.filter(Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.flag.in_([1, 2]),
                                            Question.question_to.in_([item.user for item in DiscoverList.query.filter(DiscoverList.user!=None).all()])
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(func.count(Upvote.id).desc(), Question.score.desc()
                                            ).offset(offset
                                            ).limit(limit
                                            ).all()
        question_dicts = questions_to_dict(questions, cur_user_id)
        question_dicts = [{'type':'question', 'question':question_dict} for question_dict in question_dicts]
        
        count = len(question_dicts)
        next_index = -1 if count<limit else offset+limit
        return {'count':count, 'next_index':next_index, 'stream':question_dicts}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')


def get_list_feed(cur_user_id, list_id, offset=0, limit=20, list_type='featured'):
    try:
        parent_list = get_list_from_name_or_id(list_id)
        '''
        users = User.query.join(ListItem, User.id==ListItem.child_user_id
                                ).filter(ListItem.parent_list_id==parent_list.id,
                                            ListItem.deleted==False,
                                            ListItem.child_user_id!=None,
                                            ListItem.show_on_list==True,
                                            User.deleted==False
                                        ).order_by(ListItem.score
                                        ).offset(offset
                                        ).limit(1
                                        ).all()
        '''

        #users = [{'type':'user', 'user':u} for u in guest_users_to_dict(users, cur_user_id)] if users else []
        users = []

        if list_type == 'featured':
            questions = get_featured_questions(cur_user_id, parent_list.id, offset=offset, limit=3)['stream']

            posts = Post.query.filter(Post.deleted==False,
                            Post.answer_author.in_(get_list_user_ids(parent_list.id))
                            ).order_by(Post.id.desc()).offset(offset).limit(limit-len(users)-len(questions)).all()
        
        if list_type == 'popular':
            questions = get_trending_questions(cur_user_id, parent_list.id, offset=offset, limit=3)['stream']

            posts = Post.query.filter(Post.deleted==False,
                            Post.answer_author.in_(get_list_user_ids(parent_list.id))
                            ).order_by(Post.view_count.desc()).offset(offset).limit(limit-len(users)-len(questions)).all()


        posts = [{'type':'post', 'post':p} for p in posts_to_dict(posts, cur_user_id)] if posts else []
        stream = posts
        for item in users+questions:
            idx = random.randint(0, len(stream))
            stream.insert(idx, item)

        next_index = -1 if len(stream)<limit else offset+limit
        return {'stream':stream, 'count':len(stream), 'next_index':next_index}

    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('List has been deleted or does not exit')


def suggest_answer_author(question_body):
    users = User.query.filter(User.username.in_(['arvindkejriwal', 'javedakhtar', 'ranveerbrar'])).all()
    return {'count':len(users), 'users':[thumb_user_to_dict(user) for user in users]}







