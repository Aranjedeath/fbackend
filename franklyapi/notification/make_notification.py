import datetime
import time

from models import User, Question, Notification, Post, Upvote, \
                    UserNotification, UserPushNotification, UserNotificationInfo,\
                    AccessToken
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

    gcm_ids = []
    apn_ids = []
    
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
        if get_device_type(device.device_id)=='android':
            gcm_ids.append(device.push_id)
        if get_device_type(device.device_id)=='ios':
            apn_ids.append(device.push_id)

    notification_group_id = {}
    notification = Notification.query.get(notification_id)
    group_id = int(str(notification_group_id.get(notification.type, 99))+str(int(notification.object_id, 16)))
    
    payload = {
                    "user_to" : user_id,
                    "type" : 1,
                    "id" : user_push_notification.id,
                    "text" : notification.text,
                    "icon" : None,
                    "group_id": group_id,
                    "link" : notification.link,
                    "deeplink" : notification.link,
                    "timestamp" : int(time.mktime(user_push_notification.added_at.timetuple())),
                    "seen" : False,
                    "heading":"Frankly.me"
                }

    if gcm_ids:
        pass
        print gcm_ids, payload
        gcm_sender.send_message(gcm_ids, payload)



def notification_question_ask(question_id):
    notification_type = 'question-ask-self_user'
    question = Question.query.get(question_id)
    users = User.query.filter(User.id.in_([question.question_to, question.question_author])).all()
    for u in users:
        if u.id == question.question_author:
            question_author = u
        if u.id == question.question_to:
            question_to = u

    text = "<question_author_name> asked you '<question_body>'"
    text = text.replace('<question_author_name>', question_author.first_name)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<question_to_name>', question_to.first_name)
    text = text.replace('<question_to_username>', question_to.username)
    text = text.replace('<question_author_username>', question_author.username)

    icon = None

    link = config.WEB_URL + '/question/view/{question_id}'.format(question_id=question_id)

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
    text = "<answer_author_name> answered your question"
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




'''

text_config = {
            "question-ask":{
                            "text":"<question_author_name> asked you a question",
                            "promote_text":"<question_author_name> asked <question_to_name> a question"
            },

            "post-add":{
                        "text":"<answer_author_name> answered your question",
                        "promote_text":"<answer_author_name> answered '<question_body>'"
            },

            "user_follow":{
                            "text":"<follower_name> is now following you",
                            "promote_text":"<follower_name> is now following <followed_name>"
            },

            "post-comment":{
                            "text":"<comment_author_name> commented on your answer",
                            "also_commented_text":"<comment_autho_name> also commented on an answer"
            },

            "question-upvote":{
                                "text":"<upvoted_name> upvoted your question"
            }
}


def get_text(notification_type, promote=False):
    if promote:
        return text_config['notification_type']['promote_text']
    return text_config['notification_type']['text']

def notification_question_ask(question_id, promote=False):
    notification_type = 'question-ask'
    question = Question.query.get(question_id)
    users = User.query.with_entities('username', 'first_name').filter(User.id.in_([question.question_to, question.question_author])).all()

    for u in users:
        if u.id == question.question_author:
            question_author = u
        if u.id == question.question_to:
            question_to = u

    text = get_text(notification_type=notification_type, promote=promote)
    
    text = text.replace('<question_author_name>', question_author.first_name)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<question_to_name>', question_to.first_name)
    text = text.replace('<question_to_username>', question_to.username)
    text = text.replace('<question_author_username>', question_author.username)

    icon = 'default- - -frankly_logo'

    link = config.WEB_URL + '/question/view/{question_id}'.format(question_id=question_id)

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=question_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    return notification


def notification_post_add(post_id, push_to='all', promote=False):
    notification_type = 'post-add'
    post = Post.query.get(post_id)
    question = Question.query.get(question_id)
    users = User.query.with_entities('username', 'first_name').filter(User.id.in_([post.answer_author, post.question_author])).all()

    for u in users:
        if u.id == post.question_author:
            question_author = u
        if u.id == post.answer_author:
            answer_author = u

    text = get_text(notification_type=notification_type, promote=promote)
    
    text = text.replace('<question_author_name>', question_author.first_name)
    text = text.replace('<question_author_username>', question_author.username)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<answer_author_name>', answer_author.first_name)
    text = text.replace('<answer_author_username>', answer_author.username)

    icon = 'default- - -frankly_logo'

    link = config.WEB_URL + '/question/view/{question_id}'.format(question_id=question_id)

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=post_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    return notification

def user_follow_add(followed, follower, promote=False):
    follower = User.query.get(follower)
    followed = User.query.get(followed)

    

'''

