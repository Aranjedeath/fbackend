import datetime
import time
import random

from models import User, Question, Notification, Post, Upvote, \
                    UserNotification, UserPushNotification, UserNotificationInfo,\
                    AccessToken, Follow
from configs import config
from database import get_item_id
from app import db


def add_notification_for_user(notification_id, user_ids, list_type, push_at=datetime.datetime.now()):
    for user_id in user_ids:
        user_notification = UserNotification(notification_id=notification_id, user_id=user_id,
                                             list_type=list_type, push_at=push_at,
                                             seen_at=None, seen_type=None,
                                             added_at=datetime.datetime.now(),
                                             show_on='all',
                                             id=get_item_id()
                                            )
        db.session.add(user_notification)
        db.session.commit()

        if push_at:
            push_notification(notification_id, user_id)


def push_notification(notification_id, user_id, source='application'):
    from controllers import get_device_type
    from GCM_notification import GCM
    gcm_sender = GCM()


    notification = Notification.query.get(notification_id)

    group_id = '-'.join([str(notification.type), str(notification.object_id)])
    for device in AccessToken.query.filter(AccessToken.user==user_id,
                                            AccessToken.active==True,
                                            AccessToken.push_id!=None).all():
        
        user_push_notification = UserPushNotification(
                                                      notification_id=notification_id,
                                                      user_id=user_id,
                                                      device_id=device.device_id,
                                                      push_id=device.push_id,
                                                      added_at=datetime.datetime.now(),
                                                      pushed_at=datetime.datetime.now(),
                                                      clicked_at=None,
                                                      source=source,
                                                      cancelled=False,
                                                      result=None,
                                                      id=get_item_id()
                                                     )
        db.session.add(user_push_notification)
        db.session.commit()
        payload = {
                    "user_to" : user_id,
                    "type" : 1,
                    "id" : user_push_notification.id,
                    "text" : notification.text.replace('<b>', '').replace('</b>', ''),
                    "styled_text":notification.text,
                    "icon" : None,
                    "group_id": group_id,
                    "link" : notification.link,
                    "deeplink" : notification.link,
                    "timestamp" : int(time.mktime(user_push_notification.added_at.timetuple())),
                    "seen" : False,
                    "heading":"Frankly.me"
                }
        if get_device_type(device.device_id)=='android':
            gcm_sender.send_message([device.push_id], payload)
        
        if get_device_type(device.device_id)=='ios':
            pass



def notification_question_ask(question_id):
    notification_type = 'question-ask-self_user'
    question = Question.query.get(question_id)
    users = User.query.filter(User.id.in_([question.question_to, question.question_author])).all()
    for u in users:
        if u.id == question.question_author:
            question_author = u
        if u.id == question.question_to:
            question_to = u

    text = "<b><question_author_name></b> asked you '<question_body>'"
    if question.is_anonymous:
        text = text.replace('<question_author_name>', 'Anonymous')
    else:
        text = text.replace('<question_author_name>', question_author.first_name)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<question_to_name>', question_to.first_name)
    text = text.replace('<question_to_username>', question_to.username)
    text = text.replace('<question_author_username>', question_author.username)

    icon = None

    link = config.WEB_URL + '/q/{question_id}'.format(question_id=question_id)

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=question_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    add_notification_for_user(notification_id=notification.id,
                                user_ids=[question_to.id],
                                list_type='me',
                                push_at=datetime.datetime.now()
                            )
    

    return notification


def notification_post_add(post_id):
    post = Post.query.get(post_id)
    users = User.query.filter(User.id.in_([post.answer_author, post.question_author])).all()

    for u in users:
        if u.id == post.question_author:
            question_author = u
        if u.id == post.answer_author:
            answer_author = u

    notification_type = 'post-add-self_user'
    text = "<b><answer_author_name></b> answered your question"
    text = text.replace('<answer_author_name>', answer_author.first_name)
    icon = None
    link = config.WEB_URL + '/p/{client_id}'.format(client_id=post.client_id)
    
    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=post_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()


    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question, Upvote.downvoted==False).all()]

    add_notification_for_user(notification_id=notification.id,
                                user_ids=list(set([question_author.id]+upvoters)),
                                list_type='me',
                                push_at=datetime.datetime.now()
                            )
    

    return notification


def notification_user_follow(follow_id):
    follow = Follow.query.filter(Follow.id==follow_id, Follow.deleted==False)
    users = User.query.filter(User.id.in_([follow.user, follow.followed])).all()

    for u in users:
        if u.id == follow.followed:
            followed_user = u
        if u.id == follow.user:
            follower = u

    notification_type = 'user-follow-self_user'
    text = "<b><follower_name></b> started following you"
    text = text.replace('<follower_name>', follower.first_name)
    icon = None
    link = config.WEB_URL + '/p/{client_id}'.format(client_id=post.client_id)
    
    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=post_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()


    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question, Upvote.downvoted==False).all()]

    add_notification_for_user(notification_id=notification.id,
                                user_ids=list(set([question_author.id]+upvoters)),
                                list_type='me',
                                push_at=datetime.datetime.now()
                            )
    

    return notification


