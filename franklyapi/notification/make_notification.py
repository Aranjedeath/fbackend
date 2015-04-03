from models import User, Question, Notification, Post, Upvote, \
                   Follow, UserNotificationInfo
from database import get_item_id
from app import db
from configs import config
from notification import helper, user_notification as un
from sqlalchemy.orm.exc import NoResultFound

import datetime

key = helper.key


def notification_logger(notification_type, text, link, object_id,
                        icon, for_users, manual=False, created_at=datetime.datetime.now(),
                        list_type='me', push_at=None):

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=object_id,
                                icon=icon, created_at=created_at,
                                manual=manual, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    un.add_notification_for_user(notification_id=notification.id, for_users=for_users,
                                 list_type=list_type,
                                 push_at=push_at)
    return notification

'''Creates an in-app notification
for a new question that has been
asked to the user'''


def ask_question(question_id, notification_type='question-ask-self_user'):

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

    ''' Decide pushing notification on the basis
    of user's popularity'''
    try:
        delay_push = UserNotificationInfo.query.filter(UserNotificationInfo.user_id ==
                                                       question_to.id).one().is_popular
    except NoResultFound:
        ''' In case of celeb user delay_push would always be true
        '''
        delay_push = 1 if question_to.user_type == 2 else 0


    notification = notification_logger(notification_type=notification_type, text=text, link=link,
                                       object_id=question_id, icon=icon, for_users=[question_to.id],
                                       push_at=None if delay_push else datetime.datetime.now())

    return notification



''' Creates a new in-app
notification whenever a new answer is added.
The push is done later when the video is ready.
Notification is created for:
a) Question Author
b) Upvoters
c) Followers of answer author
'''


def new_post(post_id, question_body="", notification_type='post-add-self_user'):


    k = key[notification_type]
    post = Post.query.get(post_id)
    users = User.query.filter(User.id.in_([post.answer_author, post.question_author])).all()

    for u in users:
        if u.id == post.question_author:
            question_author = u
        if u.id == post.answer_author:
            answer_author = u


    text = helper.post_add(answer_author=answer_author.firt_name, question_body=question_body)

    icon = answer_author.profile_picture

    link = k['url'] % post.client_id

    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question,
                                                              Upvote.downvoted==False).all()]

    upvoters = list(set([question_author.id]+upvoters))

    notification = notification_logger(notification_type=notification_type, text=text, link=link,
                                       object_id=post_id, icon=icon, for_users=upvoters)

    following_answered_question(post_id=post_id, question_body=question_body, author_id=answer_author.id)
    return notification


''' Create in-app notifications for users who are
    following another user who has
    answered a question
'''


def following_answered_question(post_id, author_id, question_body, notification_type='post-add-following_user'):

    k = key[notification_type]

    author = User.query.filter(User.id == author_id).one()

    text = helper.following_answered_question(question_body=question_body, author_name=author.first_name)

    link = k['url'] % post_id

    icon = author.profile_picture

    followers = Follow.query.with_entities(Follow.followed).filter(Follow.followed == author_id).all()
    user_ids = [f[0] for f in followers]

    notification = notification_logger(notification_type=notification_type, text=text, link=link,
                                       object_id=post_id, icon=icon, for_users=followers)

    return notification


''' Sent if the user's question is becoming popular
on count of number of upvotes received
'''
def share_popular_question(user_id, question_id, upvote_count, question_body,
                           notification_type='post-add-following_user'):

    text = helper.popular_question_text(question_body=question_body, upvote_count=upvote_count)
    k = key[notification_type]
    link = k['url'] % question_id

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=question_id,
                                icon=None, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    add_notification_for_user(notification_id=notification.id,
                                user_ids=[user_id],
                                list_type='me',
                                push_at=datetime.datetime.now()
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


'''Generic method for sending all sorts of milestone
notifications'''
def send_milestone_notification(milestone_name, milestone_crossed, object_id, user_id):
    '''
    read notification by notification_type
        and send it to user
    '''
    text = helper.milestone_text(milestone_name, milestone_crossed)

    link = key[milestone_name]['url'] % object_id

    notification = Notification(type=(milestone_name+'_'+milestone_crossed), text=text,
                                link=link, object_id=user_id,
                                icon=None, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    add_notification_for_user(notification_id=notification.id,
                                user_ids=[user],
                                list_type='me',
                                push_at=datetime.datetime.now())

''' Notification for requests to
update the profile'''


def user_profile_request(user_id, request_by, request_id, request_type=config.REQUEST_TYPE):

    request_by = User.query.filter(User.id == request_by).one()

    k = key[request_type]

    text = helper.user_profile_request(requester_name=request_by.first_name)

    icon = request_by.profile_picture

    link = k['url'] % user_id

    notification_logger(notification_type=request_type, text=text, link=link, object_id=request_id,
                        icon=icon, for_users=[user_id])


def comment_on_post(post_id, comment_id, comment_author):

    post = Post.query.filter(Post.id == post_id).one()

    comment_author = User.query.filter(User.id == comment_author).one()

    notification_type = 'comment_on_post'

    k = key[notification_type]

    text = helper.comment_on_post()

    link = k['url'] % post_id

    icon = comment_author.profile_picture

    notification = Notification(type=notification_type, text=text,
                                link=link, object_id=comment_id,
                                icon=icon, created_at=datetime.datetime.now(),
                                manual=False, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    add_notification_for_user(notification_id=notification.id,
                              user_ids=[post.answer_author, post.question_author],
                              list_type='me',
                              push_at=datetime.datetime.now())


def hack():
    user = User.query.filter(User.username == 'nititaylor').one()

    text = "Your followers want to know more about you! Answer the best ones from more than 500 questions asked to you."
    link = "http://frankly.me/answer"
    icon = None
    notification_logger(notification_type='pending-question-self_user',text=text,link=link,
                        object_id = user.id,
                        icon=icon,pushed_for=[user.id], push_at=datetime.datetime.now())