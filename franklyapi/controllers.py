import os
import random

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy.sql import text

from database import db_session

import CustomExceptions
import S3Uploader

from configs import config
from models import User, Block, Follow, Like, Post, UserArchive
from app import engine
from object_dict import user_to_dict, guest_user_to_dict

def has_blocked(user1, user2):
    return bool(Block.query.filter(or_(Block.user==user1.id, Block.blocked_user==user2.id)).filter(Block.user==user2.id, Block.blocked_user==user1.id).limit(1).count())

def get_follower_count(user_id):
    return Follow.query.filter(Follow.followed==user_id, Follow.unfollowed==False).count()

def get_following_count(user_id):
    return Follow.query.filter(Follow.user==user_id, Follow.unfollowed==False).count()

def get_answer_count(user_id):
    return Post.query.filter(Post.answer_author==user_id, Post.deleted==False).count()

def get_user_like_count(user_id):
    result = engine.execute(text("""SELECT COUNT(post_likes.id) FROM post_likes WHERE post_likes.post IN (SELECT posts.id from posts WHERE posts.answer_author=:user_id) AND post_likes.unliked=false;"""), **{'user_id':user_id})
    count = 0
    for row in result:
        count = row[0]
    return count

def get_post_like_count(post_id):
    return Like.query.filter(Like.post==post_id, Like.unliked==False).count()

def get_user_view_count(user_id):
    return random.randint(0, 100)

def get_post_view_count(post_id):
    return random.randint(0, 100)

def is_follower(user_id, current_user_id):
    if current_user_id:
        return bool(Follow.query.filter(Follow.user==current_user_id, Follow.followed==user_id, Follow.unfollowed==False).limit(1).count())
    return False

def is_following(user_id, current_user_id):
    if current_user_id:
        return bool(Follow.query.filter(Follow.user==user_id, Follow.followed==current_user_id, Follow.unfollowed==False).limit(1).count())
    return False

def user_view_profile(current_user_id, user_id, username=None):
    try:
        cur_user = None
        if current_user_id:
            cur_user = User.query.get(current_user_id)
            if (username and cur_user.username.lower() == username.lower()) or (current_user_id == user_id):
                return {'user': user_to_dict(cur_user)}

        if username:
            user = User.query.filter(User.username==username).one()
        else:
            user = User.query.get(user_id)

        if cur_user:
            if has_blocked(cur_user, user):
                raise CustomExceptions.BlockedUserException()
                
        if str(current_user_id) in config.ADMIN_USERS:
            return {'user': user_to_dict(user)}
        return {'user': guest_user_to_dict(user, cur_user)}
    
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException


def user_update_profile_form(user_id, first_name=None, bio=None, profile_picture=None, profile_video=None, cover_picture=None):
    update_dict = {}

    #user = User.objects.only('id').get(id=user_id)
    '''
    result = engine.execute(text("""SELECT username, first_name, bio, profile_picture, cover_picture, profile_video from access_tokens 
                                        where id=:user_id LIMIT 1"""), **{'user_id':user_id})
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
        user.first_name = first_name

    if bio:
        bio.replace('\n', ' ')
        bio = bio[:200]
        update_dict.update({'bio':bio})
        user.bio = bio

    if profile_video:
        if not (profile_video and cover_picture):
            raise CustomExceptions.BadRequestException()
        if not (profile_video.filename.split('.')[-1] in config.ALLOWED_VIDEO_FORMATS and cover_picture.filename.split('.')[-1] in config.ALLOWED_PICTURE_FORMATS):
            raise CustomExceptions.BadRequestException()
        
        uploader = S3Uploader.AmazonS3()
        path = '/tmp/profile_video_{0}_{1}'.format(str(user_id), str(profile_video.filename))
        profile_video.save(path)
        thumb_path = '/tmp/profile_cover_picture_{0}_{1}'.format(str(user_id), str(cover_picture.filename))
        cover_picture.save(thumb_path)
        thumbnail_ext = cover_picture.filename.split('.')[-1]
        profile_video_url = uploader.upload(path, 'answer_video', profile_video.headers.get('checksum'), profile_video.filename.split('.')[-1], user_id, thumb_path, thumbnail_ext)
        
        
        cover_picture_url = '.'.join(profile_video_url.split('.')[:-1])+'_thumb.'+thumbnail_ext
                
        os.remove(path)
        os.remove(thumb_path)

        update_dict.update({'profile_video':profile_video_url, 'cover_picture':cover_picture_url})
        user.profile_video = profile_video_url
        user.cover_picture = cover_picture_url

    if not profile_video and cover_picture:
        if not cover_picture.filename.split('.')[-1] in config.ALLOWED_PICTURE_FORMATS:
            raise CustomExceptions.BadRequestException()
        
        uploader = S3Uploader.AmazonS3()
        path = '/tmp/cover_picture_{0}_{1}'.format(str(user_id), str(cover_picture.filename))
        cover_picture.save(path)
        cover_picture_url = upload_image(path, cover_picture.headers.get('checksum'), cover_picture.filename.split('.')[-1], 'cover', user_id)
        os.remove(path)
        update_dict.update({'cover_picture':cover_picture_url})
        user.cover_picture = cover_picture_url


    if profile_picture:
        if not profile_picture.filename.split('.')[-1] in config.ALLOWED_PICTURE_FORMATS:
            raise CustomExceptions.BadRequestException()
        
        uploader = S3Uploader.AmazonS3()
        path = '/tmp/profile_picture_{0}_{1}'.format(str(user_id), str(profile_picture.filename))
        profile_picture.save(path)
        profile_picture_url = upload_image(path, profile_picture.headers.get('checksum'), profile_picture.filename.split('.')[-1], 'profile', user_id)
        os.remove(path)
        update_dict.update({'profile_picture':profile_picture_url})
        user.profile_picture = profile_picture_url


    if not update_dict:
        raise CustomExceptions.BadRequestException('Nothing to update')

    db_session.add(UserArchive(user=user,
                                username=update_dict['username'] if update_dict.get('username') else existing_values['username'],
                                first_name=update_dict['first_name'] if update_dict.get('first_name') else existing_values['first_name'],
                                profile_picture=update_dict['profile_picture'] if update_dict.get('profile_picture') else existing_values['profile_picture'],
                                cover_picture=update_dict['cover_picture'] if update_dict.get('cover_picture') else existing_values['cover_picture'],
                                profile_video=update_dict['profile_video'] if update_dict.get('profile_video') else existing_values['profile_video']
                                )
                    )

    User.query.filter(User.id==user_id).update(update_dict)

    db_session.commit()

    return user_to_dict(user)


def user_follow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot follow yourself")

    engine.execute(text("""INSERT INTO user_follows (user, followed, unfollowed) 
                            VALUES(:cur_user_id, :user_id, false) 
                            ON DUPLICATE KEY 
                            UPDATE unfollowed = false"""), **{'cur_user_id':cur_user_id,
                                                                            'user_id':user_id}
                    )

    '''
    notify_args = {'user1_id': cur_user_id,'user2_id': user_id}
    cel_tasks.notify_mongo.delay('follow', **notify_args)
    '''
    return {'user_id': user_id}


def user_unfollow(cur_user_id, user_id):
    if cur_user_id == user_id:
        raise CustomExceptions.BadRequestException("Cannot unfollow yourself")

    Follow.query.filter(Follow.user==cur_user_id, Follow.followed==user_id).update({'unfollowed':True})

    '''
    notify_args = {'user1_id': cur_user_id,'user2_id': user_id}
    cel_tasks.notify_mongo.delay('follow', **notify_args)
    '''
    return {'user_id': user_id}


def user_block(cur_user_id, user_id):
    if cur_user_id == user_id:
        return {'user_id': str(cur_user_id)}
    with engine.begin() as connection:
        connection.execute(text("""UPDATE user_follows SET user_follows.unfollowed=true
                                                            WHERE (user_follows.user=:user_id AND user_follows.follows=:cur_user_id)
                                                                OR (user_follows.user=:cur_user_id AND user_follows.follows=:user_id)
                                    """), **{'user_id':user_id, 'cur_user_id':user_id})

        connection.execute(text(""" INSERT INTO user_blocks (user, blocked_user, unblocked)
                                            VALUES(:cur_user_id, :user_id, false)
                                            ON DUPLICATE KEY 
                                            UPDATE unblocked = false"""), **{'cur_user_id':cur_user_id,
                                                                                'user_id':user_id
                                                                            }
                                )

    return {'user_id': user_id}

def user_unblock(cur_user_id, user_id):
    if cur_user_id == user_id:
        return {'user_id': str(cur_user_id)}
    
    Block.query.filter(Block.user==cur_user_id, Block.blocked_user==user_id).update({'unblocked':True})
    
    return {'user_id': user_id}


 
