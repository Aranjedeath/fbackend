from models import User, Question, Notification, Post, Upvote, \
                   Follow, UserNotificationInfo
from database import get_item_id
from app import db
from configs import config
from notification import helper, user_notification as un, notification_decision
from sqlalchemy.orm.exc import NoResultFound

import datetime

key = helper.key


def notification_logger(nobject, for_users, manual=False, created_at=datetime.datetime.now(),
                        list_type='me', push_at=None):

    notification = Notification(type=nobject['notification_type'], text=nobject['text'],
                                link=nobject['link'], object_id=nobject['object_id'],
                                icon=nobject['icon'], created_at=created_at,
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

    nobject = {
        'notification_type': notification_type,
        'text': helper.question_asked_text(question=question, question_author=question_author.first_name,
                                           question_to=question_to.first_name),
        'icon': question_author.profile_picture,
        'link': k['url'] % question.short_id,
        'object_id': question_id
    }

    push_now = notification_decision.decide_question_push(question_to.id, question_id)
    notification = notification_logger(nobject=nobject, for_users=[question_to.id],
                                       push_at=datetime.datetime.now() if push_now else None)

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

    nobject = {
        'object_id': post_id,
        'text':  helper.post_add(answer_author=answer_author.firt_name, question_body=question_body),
        'notification_type': notification_type,
        'icon': answer_author.profile_picture,
        'link': k['url'] % post.client_id,
    }


    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question,
                                                              Upvote.downvoted==False).all()]

    upvoters = list(set([question_author.id]+upvoters))

    notification = notification_logger(nobject=nobject, for_users=upvoters)

    following_answered_question(post_id=post_id, question_body=question_body, author_id=answer_author.id)
    return notification


''' Create in-app notifications for users who are
    following another user who has
    answered a question
'''


def following_answered_question(post_id, author_id, question_body, notification_type='post-add-following_user'):

    k = key[notification_type]

    author = User.query.filter(User.id == author_id).one()

    nobject = {
        'object_id': post_id,
        'text':   helper.following_answered_question(question_body=question_body, author_name=author.first_name),
        'notification_type': notification_type,
        'icon': author.profile_picture,
        'link': k['url'] % post_id,
    }

    try:
        following = Follow.query.with_entities(Follow.followed).filter(Follow.followed == author_id).all()
        followers = [f[0] for f in following]

        notification = notification_logger(nobject=nobject, for_users=followers)
        return notification
    except NoResultFound:
        return None




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

''' Sends out a
notification for a new celebrity that has joined the paltform.
Typically to be sent out to users who interact with a similar list
'''

def new_celebrity_user(celebrity_id=None, users=[], notification_type='new-celebrity-followed_category'):


    k = key[notification_type]

    celebrity = User.query.filter(User.id == celebrity_id).first()


    text = k['text'] % celebrity.first_name
    icon = celebrity.profile_picture
    link = k['url'] % celebrity.username


    notification_logger(notification_type=notification_type, text=text, icon=icon, link=link,
                        object_id=celebrity_id, for_users=users)


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

    nobject = {
        'notification_type': request_type,
        'text': helper.user_profile_request(requester_name=request_by.first_name),
        'icon': request_by.profile_picture,
        'link': k['url'] % user_id,
        'object_id': request_id
    }

    notification_logger(nobject=nobject, for_users=[user_id], push_at=datetime.datetime.now())


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
    users = User.query.limit(11).offset(1000)


    import controllers

    for user in users:
        print user.first_name
        controllers.question_upvote(user.id, '73c699ac929e47ff84dee366b52d75e3')

    # text = "Your followers want to know more about you! Answer the best ones from more than 500 questions asked to you."
    # link = "http://frankly.me/answer"
    # icon = None
    # notification_logger(notification_type='pending-question-self_user',text=text,link=link,
    #                     object_id = user.id,
    #                     icon=icon,pushed_for=[user.id], push_at=datetime.datetime.now())