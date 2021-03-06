import datetime

from sqlalchemy.orm.exc import NoResultFound
from models import User, Question, Notification, Post,\
                   Upvote, Follow, UserPushNotification
from app import db
from CustomExceptions import ObjectNotFoundException
from database import get_item_id
from configs import config
from notification.commons import helper
from notification.commons import notification_decision
from notification import user_notification, push_notification as push


key = helper.key


def notification_logger(nobject, for_users, manual=False, created_at=datetime.datetime.now(),
                        list_type='me', push_at=None,k=None):

    notification = Notification(type=nobject['notification_type'], text=nobject['text'],
                                link=nobject['link'], object_id=nobject['object_id'],
                                icon=nobject['icon'], created_at=created_at,
                                manual=manual, id=get_item_id())
    db.session.add(notification)
    db.session.commit()

    user_notification.add_notification_for_user(notification_id=notification.id, for_users=for_users,
                                 list_type=list_type,
                                 push_at=push_at,k=k)
    return notification


def ask_question(question_id, notification_type='question-ask-self_user'):

    '''Creates an in-app notification
        for a new question that has been
        asked to the user'''

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


def new_post(post_id, question_body="", notification_type='post-add-self_user'):
    ''' Creates a new in-app
        notification whenever a new answer is added.
        The push is done later when the video is ready.
        Notification is created for:
        a) Question Author
        b) Upvoters
        c) Followers of answer author
        '''


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
        'text':  helper.post_add(answer_author=answer_author.first_name, question_body=question_body),
        'notification_type': notification_type,
        'icon': answer_author.profile_picture,
        'link': k['url'] % post.client_id,
    }


    upvoters = [upvote.user for upvote in Upvote.query.filter(Upvote.question==post.question,
                                                              Upvote.downvoted==False).all()]

    upvoters = list(set([question_author.id]+upvoters))

    print 'Number of upvoters: ', len(upvoters)

    notification = notification_logger(nobject=nobject, for_users=upvoters)

    following_answered_question(question_body=question_body,
                                author_id=answer_author.id, nobject=nobject, upvoters=upvoters)
    return notification


def following_answered_question(author_id, question_body, nobject, upvoters,
                                notification_type='post-add-following_user'):

    ''' Create in-app notifications for users who are
    following another user who has
    answered a question
    '''

    author = User.query.filter(User.id == author_id).one()

    nobject['text'] = helper.following_answered_question(question_body=question_body, author_name=author.first_name)
    nobject['notification_type'] = notification_type


    try:
        following = Follow.query.with_entities(Follow.user).filter(Follow.followed == author_id).all()
        followers = [f[0] for f in following if f[0] != author_id]
        followers = list(set(followers) - set(upvoters))
        print 'Number of followers who have not upovted or asked the question: ', len(followers)
        notification = notification_logger(nobject=nobject, for_users=followers)
        return notification
    except NoResultFound:
        return None




# ''' Sent if the user's question is becoming popular
# on count of number of upvotes received
# '''
# def share_popular_question(user_id, question_id, upvote_count, question_body,
#                            notification_type='post-add-following_user'):
#
#     text = helper.popular_question_text(question_body=question_body, upvote_count=upvote_count)
#     k = key[notification_type]
#     link = k['url'] % question_id
#
#     notification = Notification(type=notification_type, text=text,
#                                 link=link, object_id=question_id,
#                                 icon=None, created_at=datetime.datetime.now(),
#                                 manual=False, id=get_item_id())
#     db.session.add(notification)
#     db.session.commit()
#
#     add_notification_for_user(notification_id=notification.id,
#                                 user_ids=[user_id],
#                                 list_type='me',
#                                 push_at=datetime.datetime.now()
#                             )
#
#
#     return notification

''' Sends out a
notification for a new celebrity that has joined the paltform.
Typically to be sent out to users who interact with a similar list
'''


def new_celebrity_user(celebrity_id=None, users=[], notification_type='new-celebrity-followed_category'):

    k = key[notification_type]

    celebrity = User.query.filter(User.id == celebrity_id).first()

    nobject = {
        'notification_type': notification_type,
        'text': k['text'].replace('<celebrity_name>', celebrity.first_name),
        'icon': celebrity.profile_picture,
        'link': k['url'] % celebrity.username,
        'object_id': celebrity_id
    }

    notification_logger(nobject=nobject, for_users=users, push_at=datetime.datetime.now())


def follow_milestone(user_id):

    mobject = notification_decision.decide_follow_milestone(user_id)
    if mobject:
       send_milestone_notification(mobject['milestone_name'], mobject['milestone_crossed'], mobject['object_id'],
                                   mobject['user_id'])


def question_upvote(user_id, question_id):
    try:

        should_be_pushed = notification_decision.decide_question_push(user_id=user_id, question_id=question_id)
        if should_be_pushed:

            n = Notification.query.filter(Notification.object_id == question_id,
                                          Notification.type == 'question-ask-self_user').first()
            if n is not None:
                pushed = UserPushNotification.query.filter(UserPushNotification.notification_id == n.id,
                                                           UserPushNotification.user_id == user_id).count()

                if not pushed:
                    push.send(notification_id=n.id, user_id=user_id)
    except ObjectNotFoundException:
        pass

def post_milestone(post_id, user_id):

    mobject = notification_decision.decide_post_milestone(post_id, user_id)
    if mobject:
       send_milestone_notification(mobject['milestone_name'], mobject['milestone_crossed'], mobject['object_id'],
                                   mobject['user_id'])


def send_milestone_notification(milestone_name, milestone_crossed, object_id, user_id):

    ''' Generic method for sending all sorts of milestone
        notifications'''

    nobject = {
        'notification_type': (milestone_name+ '_' + milestone_crossed),
        'text': helper.milestone_text(milestone_name, milestone_crossed),
        'icon': None,
        'link': key[milestone_name]['url'] % object_id,
        'object_id': object_id
    }

    notification_logger(nobject=nobject, for_users=[user_id], push_at=datetime.datetime.now(), k=key[milestone_name])

''' Notification for requests to
update the profile'''


def user_profile_request(user_id, request_for, request_id, request_type=config.REQUEST_TYPE):


    users = User.query.filter(User.id.in_([user_id, request_for])).all()

    for u in users:
        if u.id == user_id:
            request_by = u
        if u.id == request_for:
            requested = u

    k = key[request_type]

    nobject = {
        'notification_type': request_type,
        'text': helper.user_profile_request(requester_name=request_by.first_name),
        'icon': request_by.profile_picture,
        'link': k['url'] % request_for,
        'object_id': request_id
    }


    notification_logger(nobject=nobject, for_users=[requested.id], push_at=datetime.datetime.now())



def comment_on_post(post_id, comment_id, comment_author, notification_type='comment-add-self_post'):

    post = Post.query.filter(Post.id == post_id).one()
    if (comment_author != post.answer_author):
        comment_author = User.query.filter(User.id == comment_author).one()

        k = key[notification_type]

        nobject = {
            'notification_type': notification_type,
            'text': ("<b>%s</b> just commented on your answer." % comment_author.first_name),
            'icon': comment_author.profile_picture,
            'link': k['url'] % post_id,
            'object_id': comment_id
        }

        notification_logger(nobject=nobject, for_users=[post.answer_author], push_at=datetime.datetime.now())