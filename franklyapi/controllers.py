import random

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import or_
from sqlalchemy.sql import text


import CustomExceptions
from models import User, Block, Follow, Like, Post
from app import engine
from object_dict import user_to_dict, guest_user_to_dict

def has_blocked(user1, user2):
    return bool(Block.query.filter(or_(Block.user==user1.id, Block.blocked_user==user2.id)).filter(Block.user==user2.id, Block.blocked_user==user1.id).limit(1).count())

def get_follower_count(user_id):
    return Follow.query.filter(Follow.followed==user_id).count()

def get_following_count(user_id):
    return Follow.query.filter(Follow.user==user_id).count()

def get_answer_count(user_id):
    return Post.query.filter(Post.answer_author==user_id, Post.deleted==False).count()

def get_user_like_count(user_id):
    result = engine.execute(text("""SELECT COUNT(post_likes.id) FROM post_likes WHERE post_likes.post IN (SELECT posts.id from posts WHERE posts.answer_author=:user_id);"""), **{'user_id':user_id})
    count = 0
    for row in result:
        count = row[0]
    return count

def get_post_like_count(post_id):
    return Like.query.filter(Like.post==post_id).count()

def get_user_view_count(user_id):
    return random.randint(0, 100)

def get_post_view_count(post_id):
    return random.randint(0, 100)

def is_follower(user_id, current_user_id):
    if current_user_id:
        return bool(Follow.query.filter(Follow.user==current_user_id, Follow.followed==user_id).limit(1).count())
    return False

def is_following(user_id, current_user_id):
    if current_user_id:
        return bool(Follow.query.filter(Follow.user==user_id, Follow.followed==current_user_id).limit(1).count())
    return False



def user_view_profile(current_user_id, user_id, username=None):
    try:
        from app import ADMIN_USERS
        cur_user = None
        if current_user_id:
            cur_user = User.query.get(int(current_user_id))
            if (username and cur_user.username.lower() == username.lower()) or (current_user_id == user_id):
                return {'user': user_to_dict(cur_user)}

        if username:
            user = User.query.filter(User.username==username).one()
        else:
            user = User.query.get(int(user_id))

        if cur_user:
            if has_blocked(cur_user, user):
                raise CustomExceptions.BlockedUserException()
                
        if str(current_user_id) in ADMIN_USERS:
            return {'user': user_to_dict(user)}
        return {'user': guest_user_to_dict(user, cur_user)}
    
    except NoResultFound:
        raise CustomExceptions.UserNotFoundException
