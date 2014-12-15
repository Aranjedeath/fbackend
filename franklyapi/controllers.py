import os
import random
import datetime
import time
import hashlib
import uuid
import traceback
import sys

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.sql import text

import CustomExceptions
import media_uploader
import async_encoder
import social_helpers

from configs import config
from models import User, Block, Follow, Like, Post, UserArchive, AccessToken,\
                     Question, Upvote, Comment, ForgotPasswordToken, Install, Video
from app import redis_client, raygun, db

from object_dict import user_to_dict, guest_user_to_dict,\
                        thumb_user_to_dict, question_to_dict, post_to_dict, comment_to_dict,\
                        comments_to_dict, posts_to_dict, make_celeb_questions_dict


def check_access_token(access_token, device_id):
    try:
        print access_token, device_id
        device_type = get_device_type(device_id)
        user_id = None
        if device_type == 'web':
            user_id = redis_client.get(access_token)
            return User.query.get(user_id) if user_id else None

        access_token_object = AccessToken.query.filter(AccessToken.access_token==access_token,
                                                        AccessToken.device_id==device_id,
                                                        AccessToken.active==True).one()

        user_id = access_token_object.user
        user = User.query.get(user_id)
        print 'LOGGED IN USER', user.username
        return user
    except NoResultFound:
        return None
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
    username = username.replace(' ', '_')
    for char in username:
        if char not in config.ALLOWED_CHARACTERS:
            username = username.replace(char, '') 
    return username 

def make_username(email, full_name=None, social_username=None):
    username = ''
    uname_valid = False
    if full_name:
        username = sanitize_username(full_name)
        num_of_attempt = 0
        while not uname_valid and num_of_attempt<3:
            uname_valid = username_available(username)
            num_of_attempt += 1
            if len(username)<6:
                username = username+str(random.randint(0, 9000))

    if not uname_valid and social_username:
        username = sanitize_username(social_username)
        num_of_attempt = 0
        while not uname_valid and num_of_attempt<3:
            uname_valid = username_available(username)
            num_of_attempt += 1
            if len(username)<6:
                username = username+str(random.randint(0, 9000))

    if not uname_valid and email:
        username = sanitize_username(email.split('@')[0])
        num_of_attempt = 0
        while not uname_valid and num_of_attempt<3:
            uname_valid = username_available(username)
            num_of_attempt += 1
            if len(username)<6:
                username = username+str(random.randint(0, 9000))

    if not uname_valid:
        suffix = random.choice(['red', 'big', 'small', 'pink', 'thin', 'smart', 'genius', 'black', 'evil'])
        prefix = random.choice(['tomato', 'potato', 'cup', 'rabbit', 'bowl', 'book', 'ball', 'wall', 'chocolate'])
        username = '%s_%s'%(suffix,prefix)
        num_of_attempt = 0
        while not uname_valid and num_of_attempt<3:
            uname_valid = username_available(username)
            num_of_attempt += 1
            if len(username)<6:
                username = username+str(random.randint(0, 9000))
    return username


def generate_access_token(user_id, device_id=None):
    return hashlib.sha1('%s%s' % (user_id, int(time.time()))).hexdigest()

def set_access_token(device_id, device_type, user_id, access_token, push_id=None):
    from app import redis_client
    if device_type == 'web':
        redis_client.setex(access_token, str(user_id), 3600*24*10)
        return
    print {'device_id':device_id, 'device_type':device_type ,'access_token':access_token, 'user_id':user_id, 'push_id':push_id, 'last_login':datetime.datetime.now()}
    db.session.execute(text("""INSERT INTO access_tokens (access_token, user, device_id, device_type, active, push_id, last_login) 
                                VALUES(:access_token, :user_id, :device_id, :device_type, true, :push_id, :last_login) 
                                ON DUPLICATE KEY 
                                UPDATE access_token=:access_token, user=:user_id, active=true, push_id=:push_id, last_login=:last_login"""
                                ),
                        params={'device_id':device_id, 'device_type':device_type ,'access_token':access_token, 'user_id':user_id, 'push_id':push_id, 'last_login':datetime.datetime.now()}
                        )
    db.session.commit()


def get_data_from_external_access_token(social_type, external_access_token, external_token_secret=None):
    print external_access_token
    user_data = social_helpers.get_user_data(social_type, external_access_token, external_token_secret)
    print user_data
    if not user_data:
        raise CustomExceptions.BadRequestException('Invalid access_tokens')
    return user_data

def get_user_from_social_id(social_type, social_id):
    try:
        if social_id == 'facebook':
            return User.query.filter(User.facebook_id==social_id).one()
        elif social_id == 'google':
            return User.query.filter(User.google_id==social_id).one()
        elif social_id == 'twitter':
            return User.query.filter(User.twitter_id==social_id).one()
    except NoResultFound:
        return None

def get_device_type(device_id):
    if len(device_id)<17:
        if 'web' in device_id:
            return 'web'
        return 'android'
    return 'ios'

def new_registration_task(user_id):
    # add any task that should be done for a first time user
    pass

def register_email_user(email, password, full_name, device_id, username=None, phone_num=None,
                        push_id=None, gender=None, user_type=0, user_title=None, 
                        lat=None, lon=None, location_name=None, country_name=None, country_code=None):
    
    if not email_available(email):
        raise CustomExceptions.UserAlreadyExistsException("A user with that email already exists")

    if username and not username_available(username):
        raise CustomExceptions.UserAlreadyExistsException("A user with that username already exists")
    elif not username:
        username = make_username(email, full_name)

    device_type = get_device_type(device_id)
    registered_with = device_type + '_email'

    new_user = User(email=email, username=username, first_name=full_name, password=password, 
                registered_with=registered_with, user_type=user_type, gender=gender, user_title=user_title,
                phone_num=phone_num, lat=lat, lon=lon, location_name=location_name, country_name=country_name,
                country_code=country_code)
    db.session.add(new_user)
    db.session.commit()
    access_token = generate_access_token(new_user.id, device_id)
    set_access_token(device_id, device_type, new_user.id, access_token, push_id)
    new_registration_task(new_user.id)
    
    return {'access_token': access_token, 'username': username, 'id':new_user.id, 'new_user' : True}


def login_user_social(social_type, social_id, external_access_token, device_id, push_id=None, 
                        external_token_secret = None, user_type=0, user_title=None):
    user_data = get_data_from_external_access_token(social_type, external_access_token, external_token_secret)
    if user_data['social_id']!=social_id:
        raise CustomExceptions.InvalidTokenException("Could not verify %s token"%social_type)

    user = get_user_from_social_id(social_type, social_id)
    device_type = get_device_type(device_id)

    update_dict = {'deleted':False, '%s_token'%(social_type):external_access_token, '%s_id'%(social_type):social_id}

    if social_type == 'twitter':
            update_dict.update({'twitter_secret':external_token_secret})

    if social_type in ['facebook', 'google']:
        try:
            user = User.query.filter(User.email==user_data['email']).one()
        except NoResultFound:
            pass

    if user:
        access_token = generate_access_token(user.id, device_id)
        set_access_token(device_id, device_type, user.id, access_token, push_id)
        activated_now=user.deleted
        User.query.filter(User.id==user.id).update(update_dict)
        return {'access_token': access_token, 'id':user.id, 'username':user.username, 'activated_now': activated_now, 'new_user' : False} 
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

        return {'access_token': access_token, 'id':new_user.id, 'username':new_user.username, 'activated_now':False, 'new_user' : True} 

def login_email_new(user_id, id_type, password, device_id, push_id=None):
    try:
        if id_type=='email':
            user = User.query.filter(User.email==user_id).one()
        elif id_type=='username':
            user = User.query.filter(User.username==user_id).one()
        else:
            raise Exception("id_type should be in ['email', 'username']")
        
        access_token = generate_access_token(user.id, device_id)
        device_type = get_device_type(device_id)
        set_access_token(device_id, device_type, user.id, access_token, push_id)
        activated_now = user.deleted
        if activated_now:
            User.query.filter(User.id==user.id).update({'deleted':False})
        return {'access_token': access_token, 'username': user.username, 'activated_now': activated_now, 'id':user.id, 'new_user':True}
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException("No user with the given %s found"%(id_type))


def has_blocked(cur_user_id, user_id):
    return bool(Block.query.filter(or_(Block.user==cur_user_id, Block.blocked_user==cur_user_id)).filter(Block.user==user_id, Block.blocked_user==user_id).limit(1).count())

def get_follower_count(user_id):
    return Follow.query.filter(Follow.followed==user_id, Follow.unfollowed==False).count()

def get_following_count(user_id):
    return Follow.query.filter(Follow.user==user_id, Follow.unfollowed==False).count()

def get_answer_count(user_id):
    return Post.query.filter(Post.answer_author==user_id, Post.deleted==False).count()

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

def get_user_view_count(user_id):
    return random.randint(0, 100)

def is_following(user_id, current_user_id):
    return bool(Follow.query.filter(Follow.user==current_user_id, Follow.followed==user_id, Follow.unfollowed==False).limit(1).count())

def is_follower(user_id, current_user_id):
    return bool(Follow.query.filter(Follow.user==user_id, Follow.followed==current_user_id, Follow.unfollowed==False).limit(1).count())

def get_post_like_count(post_id):
    return Like.query.filter(Like.post==post_id, Like.unliked==False).count()

def is_liked(post_id, user_id):
    return bool(Like.query.filter(Like.post==post_id, Like.user==user_id, Like.unliked==False).count())

def get_comment_count(post_id):
    return Comment.query.filter(Comment.on_post==post_id, Comment.deleted==False).count()

def get_post_view_count(post_id):
    return random.randint(0, 100)

def get_question_upvote_count(question_id):
    return Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False).count()

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


def get_thumb_users(user_ids):
    data = {}
    if user_ids:
        result = db.session.execute(text("""SELECT id, username, first_name, profile_picture, deleted,
                                                lat, lon, location_name, country_name, country_code,
                                                gender, bio, allow_anonymous_question, user_type, user_title 
                                            FROM users 
                                            WHERE id in (:user_ids)"""),
                                        params={'user_ids':set(user_ids)})
        
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
                                                'coordinate_point':coordinate_point,
                                                'location_name':row[7],
                                                'country_name':row[8],
                                                'country_code':row[9]
                                                },
                                    'gender':row[10],
                                    'bio':row[11],
                                    'allow_anonymous_question':bool(row[12]),
                                    'user_type':row[13],
                                    'user_title':row[14]
                                    }
                        })
    return data

def user_view_profile(current_user_id, user_id, username=None):
    try:
        cur_user = None
        if current_user_id:
            cur_user = User.query.get(current_user_id)
            if (username and cur_user.username.lower() == username.lower()) or (current_user_id == user_id):
                print user_to_dict(cur_user)
                return {'user': user_to_dict(cur_user)}

        if username:
            user = User.query.filter(User.username==username).one()
        else:
            user = User.query.get(user_id)

        if cur_user:
            if has_blocked(cur_user.id, user.id):
                raise CustomExceptions.BlockedUserException()
        if str(current_user_id) in config.ADMIN_USERS:
            return {'user': user_to_dict(user)}
        return {'user': guest_user_to_dict(user, current_user_id)}
    
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException


def user_update_profile_form(user_id, first_name=None, bio=None, profile_picture=None, profile_video=None, cover_picture=None, user_type=None, user_title=None, phone_num=None):
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
                        'profile_video':user.profile_video
                        }

    if first_name:
        update_dict.update({'first_name':first_name})

    if bio:
        bio.replace('\n', ' ')
        bio = bio[:200]
        update_dict.update({'bio':bio})

    if profile_video:
        profile_video_url, cover_picture_url = media_uploader.upload_user_video(user_id=user_id, video_file=profile_video, video_thumbnail_file=cover_picture, video_type='profile_video')
        update_dict.update({'profile_video':profile_video_url, 'cover_picture':cover_picture_url})
        add_video_to_db(profile_video_url, cover_picture_url)
        async_encoder.encode_video_task.delay(profile_video_url)

    if not profile_video and cover_picture:
        cover_picture_url = media_uploader.upload_user_image(user_id=user_id, image_file=cover_picture, image_type='cover_picture')
        update_dict.update({'cover_picture':cover_picture_url})

    if profile_picture:
        tmp_path = '/tmp/request/{random_string}.jpeg'.format(random_string=uuid.uuid1().hex)
        profile_picture.save(tmp_path)
        profile_picture_url = media_uploader.upload_user_image(user_id=user_id, image_file_path=tmp_path, image_type='profile_picture')
        update_dict.update({'profile_picture':profile_picture_url})
        os.remove(tmp_path)

    if not update_dict:
        raise CustomExceptions.BadRequestException('Nothing to update')
    db.session.add(UserArchive(user=user,
                                username=update_dict['username'] if update_dict.get('username') else existing_values['username'],
                                first_name=update_dict['first_name'] if update_dict.get('first_name') else existing_values['first_name'],
                                profile_picture=update_dict['profile_picture'] if update_dict.get('profile_picture') else existing_values['profile_picture'],
                                cover_picture=update_dict['cover_picture'] if update_dict.get('cover_picture') else existing_values['cover_picture'],
                                profile_video=update_dict['profile_video'] if update_dict.get('profile_video') else existing_values['profile_video'],
                                bio=update_dict['bio'] if update_dict.get('profile_video') else existing_values['bio']
                                )
                    )
    print update_dict
    
    User.query.filter(User.id==user_id).update(update_dict)
    db.session.commit()

    

    return user_to_dict(user)


def user_follow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot follow yourself")

    db.session.execute(text("""INSERT INTO user_follows (user, followed, unfollowed) 
                                VALUES(:cur_user_id, :user_id, false) 
                                ON DUPLICATE KEY 
                                UPDATE unfollowed = false"""),
                        params={'cur_user_id':cur_user_id, 'user_id':user_id}
                    )
    db.session.commit()
    '''
    notify_args = {'user1_id': cur_user_id,'user2_id': user_id}
    cel_tasks.notify_mongo.delay('follow', **notify_args)
    '''
    return {'user_id': user_id}


def user_unfollow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot unfollow yourself")
    Follow.query.filter(Follow.user==cur_user_id, Follow.followed==user_id).update({'unfollowed':True})
    return {'user_id': user_id}


def user_block(cur_user_id, user_id):
    if cur_user_id == user_id:
        return {'user_id': str(cur_user_id)}
    db.session.execute(text("""UPDATE user_follows 
                                SET user_follows.unfollowed=true
                                WHERE (user_follows.user=:user_id 
                                AND user_follows.follows=:cur_user_id)
                                OR (user_follows.user=:cur_user_id 
                                    AND user_follows.follows=:user_id)"""),
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
    if username_available(new_username):
        User.query.filter(User.id==user_id).update({'username':new_username})
        return {'username':new_username, 'status':'success', 'id':str(user_id)}
    else:
        raise CustomExceptions.UnameUnavailableException('Username invalid or not available')

def user_change_password(user_id, new_password):
    if password_is_valid(new_password):
        User.query.filter(User.id==user_id).update({'password':new_password})
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

    print '**Location: ',user_id, lat, lon, country , country_code , loc_name 
   
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

    Post.query.filter(Post.answer_author==user_id, 
                        or_(Post.lat==None, (Post.lat==0.0, Post.lon==0.0))
                        ).update({  "lat":lat,
                                    "lon":lon,
                                    "location_name":loc_name,
                                    "country_code":country_code,
                                    "country_name":country
                                })

def update_push_id(cur_user_id, device_id, push_id):
    AccessToken.query.filter(   AccessToken.user==cur_user_id,
                                AccessToken.device_id==device_id
                            ).update({'push_id':push_id})



def user_update_access_token(user_id, acc_type, token):
    try:
        if acc_type=='facebook':
            user_data = get_data_from_external_access_token('facebook', token, external_token_secret=None)
            User.query.filter(User.id==user_id, User.facebook_id==user_data['social_id']).update({'facebook_token':token, 'facebook_write_permission':True})
            return {'success':True}
    
    except CustomExceptions.InvalidTokenException:
        raise CustomExceptions.BadRequestException('invalid token')


def question_ask(cur_user_id, question_to, body, lat, lon, is_anonymous): 
    if has_blocked(cur_user_id, question_to):
        raise CustomExceptions.BlockedUserException()

    user_status = get_user_status(question_to)

    if not cur_user_id == question_to and is_anonymous and not user_status['allow_anonymous_question']:
        raise CustomExceptions.NoPermissionException('Anonymous question not allowed for the user')

    public = True if user_status['user_type']==2 else False #if user is celeb

    question = Question(question_author=cur_user_id, question_to=question_to, 
                body=body.capitalize(), is_anonymous=is_anonymous, public=public, lat=lat, lon=lon)

    db.session.add(question)
    db.session.commit()
    '''
    if not bot and q.show_in_list and not user_id == kwargs['question_to']:
        notify_args = {
                        'user1_id': user.id,
                        'user2_id': question_to.id,
                        'question_id': q.id
                        }
        cel_tasks.notify_mongo.delay('question_ask', **notify_args)
    if q.question_author.monkness==-1:
            cel_tasks.remind_question.apply_async(kwargs={'question_id':q.id}, countdown=3600*72)

    if user_status['monkness']==-2:
        send_mail_to_inactive_user(question=q , friend = friend)
        return

    '''

    resp = {'success':True, 'id':str(question.id)}
    return resp


def question_list(user_id, offset, limit):

    questions_query = Question.query.filter(Question.question_to==user_id, 
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False
                                            ).order_by(Question.timestamp.desc()).offset(offset)
    
    questions = [{'question':question_to_dict(question), 'type':'question'} for question in questions_query.limit(limit)]
    next_index = str(offset+limit) if questions else "-1"
    return {'questions': questions, 'count': len(questions),  'next_index' : next_index}


def question_list_public(current_user_id, user_id, offset, limit):
    if has_blocked(current_user_id, user_id):
        raise CustomExceptions.BlockedUserException('User Not Found')

    questions_query = Question.query.filter(Question.question_to==user_id, 
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.public==True
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(func.count(Upvote.id).desc()
                                            ).offset(offset)

    questions = [{'question':question_to_dict(question), 'type':'question'} for question in questions_query.limit(limit)]
    next_index = str(offset+limit) if questions else "-1"
    return {'questions': questions, 'count': len(questions),  'next_index' : next_index}

def question_upvote(cur_user_id, question_id):
    if Question.query.filter(
                            Question.id==question_id, 
                            Question.public==True, 
                            Question.question_to!=cur_user_id,
                            Question.deleted==False
                            ).count():

        db.session.execute(text("""INSERT INTO question_upvotes (user, question, downvoted) 
                                    VALUES(:cur_user_id, :question_id, false) 
                                    ON DUPLICATE KEY 
                                    UPDATE downvoted = false"""),
                            params={'cur_user_id':cur_user_id, 'question_id':question_id}
                        )
    else:
        raise CustomExceptions.BadRequestException("Question is not available for upvote")
    
    return {'id':question_id, 'success':True}

def question_downvote(cur_user_id, question_id):
    if Question.query.filter(Question.id==question_id, Question.question_author==cur_user_id).count():
        raise CustomExceptions.BadRequestException("You cannot downvote your own question")
    result = Upvote.query.filter(Upvote.user==cur_user_id, Upvote.question==question_id).update({'downvoted':True})
    return {'id':question_id, 'success':bool(result)}


def question_ignore(user_id, question_id):
    result = Question.query.filter(  Question.id==question_id,
                            Question.question_to==user_id,
                            Question.is_answered==False,
                            Question.deleted==False
                        ).update({'is_ignored':True})

    return {"question_id":question_id, "success":bool(result)}

def post_like(cur_user_id, post_id):
    result = db.session.execute(text("""SELECT answer_author, question_author
                                        FROM posts
                                        WHERE id=:post_id, deleted=false
                                        LIMIT 1"""),
                                params={'post_id':post_id}
                        )
    row = result.fetchone()
    if not row:
        raise CustomExceptions.PostNotFoundException('Post not available for action')
    
    answer_author, question_author= row

    if not (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
        db.session.execute(text("""INSERT INTO post_likes (user, post, unliked) 
                                    VALUES(:cur_user_id, :post_id, false) 
                                    ON DUPLICATE KEY 
                                    UPDATE unliked = false"""),
                            params={'cur_user_id':cur_user_id, 'post_id':post_id}
                            )
        #send notification
        return {'id': post_id, 'success':True}

    else:
        raise CustomExceptions.PostNotFoundException('Post not available for action')

def post_unlike(cur_user_id, post_id):
    result = Like.query.filter(Like.user==cur_user_id, Like.post==post_id).update({'downvoted':True})
    return {'id':post_id, 'success':bool(result)}

def post_delete(cur_user_id, post_id):
    result = Post.query.filter(Post.id==post_id, Post.answer_author==cur_user_id, Post.deleted==False).update({'deleted':True})
    return {'id':post_id, 'success':bool(result)}

def post_view(cur_user_id, post_id, client_id=None):
    try:
        if client_id:
            post = Post.query.filter(Post.client_id==client_id, Post.deleted==False).one()
        else:
            post = Post.query.filter(Post.id==post_id, Post.deleted==False).one()

        if cur_user_id and (has_blocked(cur_user_id, post.answer_author) or has_blocked(cur_user_id, post.question_author)):
            raise CustomExceptions.BlockedUserException()

        {'post': post_to_dict(post, cur_user_id)}
    except NoResultFound:
        raise CustomExceptions.PostNotFoundException()



def comment_add(cur_user_id, post_id, body, lat, lon):
    result = db.session.execute(text("""SELECT answer_author, question_author
                                        FROM posts
                                        WHERE id=:post_id, deleted=false 
                                        LIMIT 1"""),
                                params={'post_id':post_id}
                                )
    row = result.fetchone()
    if not row:
        raise CustomExceptions.PostNotFoundException('Post not available for action')
    
    answer_author, question_author= row

    if not (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
        comment = Comment(on_post=post_id, body=body, comment_author=cur_user_id, lat=lat, lon=lon)
        db.session.add(comment)
        db.session.commit()
    
        user_update_location(cur_user_id, lat, lon, country=None, country_code=None, loc_name=None)
        '''
        notify_args = {
            'user_id': user.id,
            'comment_id': c.id,
            'mentioned_in_comment': mentions
        }

        cel_tasks.notify_mongo.delay('comment_add', **notify_args)

        try:
            if c.comment_author.facebook_token:
                fb = FBActionPublisher()
                fb.post_action_comment(c.comment_author.facebook_token, str(c.on_post.id))
        except Exception as e:
            print e
        '''
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
            return {'success': True}
        else:
            raise CustomExceptions.ObjectNotFoundException('Comment Not available for action')
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException('Comment Not available for action')


def comment_list(cur_user_id, post_id, offset, limit):
        result = db.session.execute(text("""SELECT answer_author, question_author
                                            FROM posts
                                            WHERE id=:post_id, deleted=false 
                                            LIMIT 1"""),
                                    params={'post_id':post_id}
                                    )
        row = result.fetchone()
        if not row:
            raise CustomExceptions.PostNotFoundException("Comments for this post is not available")
        answer_author, question_author= row
        
        if not (has_blocked(cur_user_id, answer_author) or has_blocked(cur_user_id, answer_author)):
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
        comments = comments_to_dict(comments)
        next_index = offset+limit if comments else -1
        return {'comments': comments, 'post': post_id, 'next_index':next_index}


def get_user_timeline(cur_user_id, user_id, offset, limit):
    if cur_user_id and has_blocked(cur_user_id, user_id):
        raise CustomExceptions.UserNotFoundException('User does not exist')
    posts_query = Post.query.filter(Post.answer_author==user_id, Post.deleted==False)
    total_count = posts_query.count()
    posts = posts_query.offset(offset).limit(limit).all()
    posts = posts_to_dict(posts)
    posts = [{'type':'post', 'post':post} for post in posts]
    next_index = offset+limit if posts else -1
    return {'stream': posts, 'count':len(posts), 'next_index':next_index, 'total':total_count}
    


def home_feed(cur_user_id, offset, limit, web):
    follows = Follow.query.filter(Follow.user==cur_user_id, Follow.unfollowed==False)
    followers = [follow.followed for follow in follows]

    posts = Post.query.filter(or_(Post.answer_author.in_(followers), Post.question_author==cur_user_id)
                    ).filter(Post.deleted==False
                    ).order_by(Post.timestamp
                    ).offset(offset
                    ).limit(limit
                    ).all()

    posts = posts_to_dict(posts)
    feeds = [{'type':'post', 'post':post} for post in posts]
    next_index = offset+limit if posts else -1
    
    skip = offset/10
    celeb_limit = 2
    
    if offset != 0:
        skip = skip+celeb_limit+1

    celeb_users = User.query.filter(User.id.in_(followers+[cur_user_id]),
                                    User.deleted==False, User.user_type==2
                                    ).order_by(User.user_since.desc()).offset(skip
                                    ).limit(celeb_limit)
    
    for user in celeb_users:
        questions_query = Question.query.filter(Question.question_to==user.id, 
                                        Question.deleted==False,
                                        Question.is_answered==False,
                                        Question.is_ignored==False,
                                        Question.public==True
                                        )
        count = questions_query.count()
        max_limit = count-2 if count>2 else count
        question_offset = random.randint(0, max_limit)
        questions = questions_query.offset(question_offset
                                    ).limit(2)
        questions_feed = []
        if web:
            questions_feed = [{'type':'question', 'questions':question_to_dict(q, cur_user_id)} for q in questions.all()]
            
        elif questions.count()==2:
            questions_feed = [{'type':'questions', 'questions':make_celeb_questions_dict(celeb_users[0], questions.all, cur_user_id)}]
        
        extra_feed = [{'type':'user', 'user':guest_user_to_dict(user, cur_user_id)}]
        print extra_feed
        if questions_feed:
            extra_feed.extend(questions_feed)

        random_index = random.randint(0, len(feeds))
        for item in extra_feed:
            feeds.insert(random_index, item)
            random_index +=1

    next_index = offset+limit if feeds else -1

    return {'stream': feeds, 'count':len(feeds), 'next_index':next_index}



def discover_posts(cur_user_id, offset, limit, web, lat=None, lon=None):
    follows = Follow.query.filter(Follow.user==cur_user_id, Follow.unfollowed==False)
    followings = [follow.followed for follow in follows]

    posts = Post.query.filter(~Post.answer_author.in_(followings+[cur_user_id])
                    ).filter(Post.deleted==False, Post.popular==True
                    ).order_by(Post.timestamp
                    ).offset(offset
                    ).limit(limit
                    ).all()

    posts = posts_to_dict(posts)
    feeds = [{'type':'post', 'post':post} for post in posts]
    next_index = offset+limit if posts else -1
    
    skip = offset/10
    celeb_limit = 2
    
    if offset != 0:
        skip = skip+celeb_limit+1
    print 'DISCOVER USERS OFFSET/LIMIT:', skip, celeb_limit
    print 'followings', followings
    celeb_users = User.query.filter(~User.id.in_(followings+[cur_user_id])
                                ).filter(User.deleted==False
                                ).order_by(User.user_since.desc()).offset(skip
                                ).limit(celeb_limit)
    
    for user in celeb_users:
        questions_query = Question.query.filter(Question.question_to==user.id, 
                                        Question.deleted==False,
                                        Question.is_answered==False,
                                        Question.is_ignored==False,
                                        Question.public==True
                                        )
        count = questions_query.count()
        max_limit = count-2 if count>2 else count
        question_offset = random.randint(0, max_limit)
        questions = questions_query.offset(question_offset
                                    ).limit(2)
        questions_feed = []
        if web:
            questions_feed = [{'type':'question', 'questions':question_to_dict(q, cur_user_id)} for q in questions.all()]
            
        elif questions.count()==2:
            questions_feed = [{'type':'questions', 'questions':make_celeb_questions_dict(celeb_users[0], questions.all, cur_user_id)}]
        
        extra_feed = [{'type':'user', 'user':guest_user_to_dict(user, cur_user_id)}]

        if questions_feed:
            extra_feed.extend(questions_feed)

        random_index = random.randint(0, len(feeds))
        for item in extra_feed:
            feeds.insert(random_index, item)
            random_index +=1
    print feeds
    next_index = offset+limit if feeds else -1

    return {'stream': feeds, 'count':len(feeds), 'next_index':next_index}


def create_forgot_password_token(username=None, email=None):
    try:
        import hashlib
        if username:
            user = User.query.filter(User.username==username).one()
        elif email:
            user = User.query.filter(User.email==email).one()
        else:
            raise CustomExceptions.BadRequestException()

        token_salt = 'ANDjdnbsjKDND=skjkhd94bwi20284HFJ22u84'
        token_string = '%s+%s+%s'%(str(user.id), token_salt, time.time())
        token = hashlib.sha256(token_string).hexdigest()
        now_time = datetime.datetime.now()
        db.session.execute(text("""INSERT INTO forgot_password_tokens (user, token, email, created_at) 
                                    VALUES(:user_id, :token, :email, :cur_time) 
                                    ON DUPLICATE KEY 
                                    UPDATE token = :token, created_at=:cur_time"""),
                            params={'user_id':user.id, 'token':token, 'email':user.email, 'cur_time':now_time}
                            )

        body = '''Hi <b>{0}</b>,<br>
Click on the link below to reset your password and start asking questions and answering them yourself.
<br>
<br>
<h3><a href='http://frankly.me/resetpassword/{1}'>Reset your password</a><br></h3>
<br>
<br>
If the link above does not work copy the url below and paste it in your browsers address bar.
<br>
<b>http://frankly.me/resetpassword/{1}</b>
<br>
If you did not request to reset your password. You can ignore this message.
<br>
If you run into any problems shoot us a mail at </a href=mailto:letstalk@frankly.me>letstalk@frankly.me</a>
<br>
Regards<br>
Franksters'''.format(user.first_name if user.first_name else user.username, token)
        subject = 'Reset your password and get back in action on Frankly.me'
        
        email_wrapper.sendMail('letstalk@frankly.me', user.email, subject, body)
        return {'success':True}
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException()


def check_forgot_password_token(token):
    try:
        token_object = ForgotPasswordToken.query.filter(ForgotPasswordToken.token==token).one()
        now_time = datetime.datetime.now()
        timediff = now_time - token_object.created_at
        if timediff.total_seconds>3600*48:
            token_object.delete()
            raise NoResultFound()
        return {'valid':True, 'token':token}
    except NoResultFound:
        return {'valid':False, 'token':token}


def reset_password(token, password):
    try:
        print datetime.strftime(datetime.datetime.now(), '%d %b %Y %I:%M:%S %p UTC')
        token_object = ForgotPasswordToken.query.filter(ForgotPasswordToken.token==token).one()
        
        now_time = datetime.now()
        timediff = now_time - token_object.created_at

        if timediff.total_seconds>3600*48:
            token_object.delete()
            raise CustomExceptions.ObjectNotFoundException()

        if len(password)<6:
            raise CustomExceptions.PasswordTooShortException()

        user_query = User.query.filter(User.id==token_object.user)

        user = user_query.one()
        user_query.update({'password':password})

        body = '''Hi <b>{0}</b>,<br>
Your password was successfully reset at {1}.
<br>
<br>
Now you can get back to the Frankly.me and start asking questions and answering them yourself.
<br>
<br>
Regards<br>
Franksters'''.format(user.first_name, datetime.strftime(datetime.datetime.now(), '%d %b %Y %I:%M:%S %p UTC'))
        subject = 'Your password has been reset'
    
        email_wrapper.sendMail('letstalk@frankly.me', token_object.email, subject, body)
        
        return {'success':True, 
                'error':None, 
                'message':'Your password has been reset'}
    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException()

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
    db.session(i)
    db.session.commit()


def get_new_client_id():
    id_chars = []
    for i in range(6):
        id_chars.append(random.choice(config.ALLOWED_CHARACTERS))
    cid = 's%s'%(''.join(id_chars))
    if not Post.query.filter(Post.client_id==cid).count():
        return cid
    return get_new_client_id()


def add_video_post(cur_user_id, question_id, video, video_thumbnail, answer_type,
                        lat=None, lon=None, client_id=get_new_client_id()):
    try:
        if cur_user_id in config.ADMIN_USERS:
            question = Question.query.filter(Question.id==question_id,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.deleted==False).one()
            answer_author = question.question_to
        else:
            answer_author = cur_user_id
            question = Question.query.filter(Question.question_to==cur_user_id,
                                            Question.id==question_id,
                                            Question.is_answered==False,
                                            Question.is_ignored==False,
                                            Question.deleted==False).one()
        
        if has_blocked(answer_author, question.question_author):
            raise CustomExceptions.BlockedUserException("Question not available for action")

        video_url, thumbnail_url = media_uploader.upload_user_video(user_id=cur_user_id, video_file=video, video_thumbnail_file=video_thumbnail, video_type='answer')
        add_video_to_db(video_url, thumbnail_url)
        post = Post(question=question_id,
                    question_author=question.question_author, 
                    answer_author=answer_author,                    
                    answer_type=answer_type,
                    media_url=video_url,
                    thumnail_url=thumbnail_url,
                    client_id=client_id,
                    lat=lat,
                    lon=lon)

        db.session(post)
        db.session.commit()
        async_encoder.encode_video_task(video_url)

        Question.query.filter(Question.id==question_id).update({'is_answered':True})

        return {'success': True, 'id': str(post.id)}

    except NoResultFound:
        raise CustomExceptions.ObjectNotFoundException("Question not available for action")



def get_notifications(cur_user_id, notification_category, offset, limit):
    #TODO: Fix this dummy function.
    return {'notifications':[], 'count':0, 'next_index':-1}

def get_notification_count(cur_user_id):
    return 0

def logout(access_token, device_id):
    from app import redis_client
    device_type = get_device_type(device_id)
    if device_type=='web':
        redis_client.delete(device_id)
        return True
    count = AccessToken.query.filter(AccessToken.access_token==access_token, AccessToken.device_id==device_id).update({'active':False})
    return bool(count)


def add_video_to_db(video_url, thumbnail_url):
    db.session.add(Video(url=video_url, thumbnail=thumbnail_url))
    db.session.commit()

def update_video_state(video_url, result={}):
    video_exists = bool(Video.query.filter(Video.url==video_url).count())
    if result and video_exists:
        result.update({'process_state':'success'})
        Video.query.filter(Video.url==video_url).update(result)
    
    elif result and not video_exists:
            result.update({'url':'video_url','process_state':'success'})
            video_object = Video(**result)
            db.session.add(video_object)
            db.session.commit()
    
    elif not result and video_exists:
        Video.query.filter(Video.url==video_url).update({'process_state':'failed'})

    else:
        result.update({'url':'video_url','process_state':'failed'})
        video_object = Video(**result)
        db.session.add(video_object)
        db.session.commit()
















