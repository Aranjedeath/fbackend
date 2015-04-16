from models import User, Question, Post, UserPushNotification, Notification, UserNotification
from app import db

import controllers
import notification_decision
import random
import datetime

v = User.query.filter(User.username == 'chimpspanner').first()
s = User.query.filter(User.username == 'shashank').first()
f = User.query.limit(random.randint(5000,8000)).all()
p = Post.query.filter(Post.answer_author == v.id, Post.deleted == False).all()

q = Question.query.filter(Question.question_to == v.id)


def cleanup():

    UserPushNotification.query.filter(UserPushNotification.user_id == v.id,
                                      UserPushNotification.added_at <
                                      (datetime.datetime.now() - datetime.timedelta(days=1))).delete()
    db.session.commit()
    print 'Done with cleanup'


def user_followed(followed=v, followers=f):

    cleanup()
    controllers.user_follow(followed.id, followers[random.randint(0, len(followers) - 1)].id)
    print 'User followed passed'


def ask_question(asker=s, asked=v, is_anon=True, from_widget=False):

    cleanup()
    controllers.question_ask(asker.id, asked.id, "Test ask questions?", 0, 0, is_anon, from_widget)
    print 'Ask question passed'


def post_like(liked_by=f[random.randint(0, len(f) - 1)].id, post_id=p[random.randint(0, len(p) - 1)].id):

    cleanup()
    print post_id
    controllers.post_like(liked_by, post_id)
    print 'Post like passed'


def comment_add(comment_by=s.id, post_id=p[random.randint(0, len(p) - 1)].id, comment="Wonderful answer"):

    cleanup()
    controllers.comment_add(comment_by, post_id, comment, 0, 0)
    print 'Comment post passed'


def new_post(post_id):

    cleanup()
    n = Notification.query.filter(Notification.object_id == post_id, Notification.type == 'post-add-self_user').first()
    UserPushNotification.query.filter(UserPushNotification.notification_id == n.id).delete()
    db.session.commit()
    notification_decision.post_notifications(post_id)
    print 'New post passed'


def main():

    user_followed()
    ask_question()
    post_like()
    comment_add()
    #new_post()



def make_data():
    from models import User, Post
    u = User.query.filter(User.username == 'chimpspanner').first()
    s = User.query.filter(User.username == 'shashank').first()
    p = Post.query.filter(Post.answer_author == s.id, Post.question_author == u.id).first()
    print p.id
    n = Notification.query.filter(Notification.object_id == p.id, Notification.type == 'post-add-self_user').first()
    print n.id
    try:
        UserPushNotification.query.filter(UserPushNotification.user_id == u.id,
                                           UserPushNotification.notification_id == n.id).delete()
        db.session.commit()
    except:
        pass
    post_notifications(p.id)
