import datetime
import time
from models import User, Question, Notification, Post, Upvote, \
                    UserNotification, UserPushNotification, UserNotificationInfo,\
                    AccessToken, Follow
from configs import config
from database import get_item_id
from app import db
from notification import helper, notification_decision
from sqlalchemy.orm.exc import NoResultFound

key = helper.key


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

def get_device_type(device_id):
    if len(device_id)<17:
        if 'web' in device_id:
            return 'web'
        return 'android'
    return 'ios'


def push_notification(notification_id, user_id, source='application'):

    if notification_decision.\
            count_of_push_notifications_sent(user_id = user_id) <= config.GLOBAL_PUSH_NOTIFICATION_DAY_LIMIT:

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
                        "notification_id": notification.id,
                        "text" : notification.text.replace('<b>', '').replace('</b>', ''),
                        "styled_text":notification.text,
                        "icon" : notification.icon,
                        "cover_image":None,
                        "is_actionable":False,
                        "group_id": group_id,
                        "link" : notification.link,
                        "deeplink" : notification.link,
                        "timestamp" : int(time.mktime(user_push_notification.added_at.timetuple())),
                        "seen" : False,
                        "heading":"Frankly.me"
                    }
            if get_device_type(device.device_id)=='android':
                from GCM_notification import GCM
                gcm_sender = GCM()
                gcm_sender.send_message([device.push_id], payload)

            if get_device_type(device.device_id)=='ios':
                from APN_notification import  APN
                apns = APN()
                apns.send_message([device.push_id],payload)



def ask_question(question_id, notification_type = 'question-ask-self_user'):

    k = key[notification_type]
    question = Question.query.get(question_id)
    users = User.query.filter(User.id.in_([question.question_to, question.question_author])).all()

    for u in users:
        if u.id == question.question_author:
            question_author = u
        if u.id == question.question_to:
            question_to = u

    text = helper.question_asked_text(question=question, question_author=question_author, question_to=question_to)

    icon = question_author.profile_picture

    link = k['url'] % question.short_id

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=question_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    ''' Decide pushing notification on the basis
    of user's popularity'''
    try:
        delay_push = UserNotificationInfo.query.filter(UserNotificationInfo.user_id ==
                                                       question_to.id).one().is_popular
    except NoResultFound:
        ''' In case of celeb user delay_push would always be true
        '''
        delay_push = 1 if question_to.user_type == 2 else 0



    add_notification_for_user(notification_id=notification.id,
                                user_ids=[question_to.id],
                                list_type='me',
                                push_at= None if delay_push else datetime.datetime.now()
                            )
    

    return notification


def new_celebrity_user(users=[], notification_id=None, celebrity_id=None):
    '''Either create a new notification or fetch a pre-existing one.
    Users would be a list that can be empty as well'''


    for user in users:
        notification.new_celebrity_user(users=[user.id], notification_id=notification_id, celebrity_id=object_id)
    if notification_id is None and celebrity_id is not None:
        celebrity = User.query.filter(User.id == celebrity_id).first()

        notification_type = "new-celeb-user"
        text = "%s just joined frankly. Be the first one to ask a question." % celebrity.first_name
        icon = celebrity.profile_picture
        link = "http://frankly.me/%s" % celebrity.username

        notification = Notification(type=notification_type, text=text,
                                    link=link, object_id=celebrity.id,
                                    icon=icon, created_at=datetime.datetime.now(),
                                    manual=False, id=get_item_id())
        db.session.add(notification)
        db.session.commit()
    else:
        notification = Notification.query.filter(Notification.id == notification_id).first()

    for user in users:
        add_notification_for_user(notification_id=notification.id,
                                user_ids=[user],
                                list_type='me',
                                push_at=datetime.datetime.now()
                            )

def new_post(post_id, question_body="", notification_type = 'post-add-self_user',
             delay_push=True):


    k = key[notification_type]
    post = Post.query.get(post_id)
    users = User.query.filter(User.id.in_([post.answer_author, post.question_author])).all()


    for u in users:
        if u.id == post.question_author:
            question_author = u
        if u.id == post.answer_author:
            answer_author = u


    text = helper.post_add(answer_author=answer_author, question_body=question_body)

    icon = answer_author.profile_picture

    link = k['url'] % post.client_id
    
    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=post_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()


    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question, Upvote.downvoted==False).all()]
    upvoters = set([question_author.id]+upvoters)


    add_notification_for_user(notification_id=notification.id,
                                user_ids=list(upvoters),
                                list_type='me',
                                push_at=None if delay_push else datetime.datetime.now()
                            )
    

    return notification

def new_comment(post_id):
    pass

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


