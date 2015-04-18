import urlparse

from models import Question, Upvote, InflatedStat, User, Follow, Like, Post, Comment, AccessToken
import time
import datetime
from app import db
from sqlalchemy.sql import text


def url_type(data):
    parts = urlparse.urlsplit(data)
    if not parts.scheme or not parts.netloc:
        raise ValueError('Not a valid url')
    return data


def get_post_like_count(post_id):
    count = Like.query.filter(Like.post == post_id, Like.unliked == False).count()
    return count


def get_post_view_count(post_id):
    view_count = Post.query.with_entities('view_count').filter(Post.id == post_id).one().view_count
    return view_count


def get_question_upvote_count(question_id):
    from math import sqrt, log
    from datetime import datetime, timedelta
    d = datetime.now() - timedelta(minutes=5)
    question = Question.query.filter(Question.id == question_id).first()
    t = question.timestamp
    time_factor = 0
    if t:
        time_factor = int(time.mktime(t.timetuple())) % 7
    count_to_pump = Upvote.query.filter(Upvote.question == question_id,
                                        Upvote.downvoted == False,
                                        Upvote.timestamp <= d
                                        ).count()

    count_as_such = Upvote.query.filter(Upvote.question == question_id,
                                        Upvote.downvoted == False,
                                        Upvote.timestamp > d
                                        ).count()

    if count_to_pump:
        count = int(11*count_to_pump + log(count_to_pump, 2) + sqrt(count_to_pump)) + count_as_such
        count += time_factor
    else:
        count = count_to_pump + count_as_such
    inflated_stat = InflatedStat.query.filter(InflatedStat.question == question_id).first()
    if inflated_stat:
        count += inflated_stat.upvote_count
    return count


def get_comment_count(post_id):
    return Comment.query.filter(Comment.on_post == post_id,
                                Comment.deleted == False
                                ).count()


def get_follower_count(user_id):
    from math import log, sqrt
    from datetime import datetime, timedelta
    user = User.query.filter(User.id == user_id).one()

    d = datetime.now() - timedelta(minutes=5)
    count_to_pump = Follow.query.filter(Follow.followed == user_id,
                                        Follow.unfollowed == False,
                                        Follow.timestamp <= d
                                        ).count()

    count_as_such = Follow.query.filter(Follow.followed == user_id,
                                        Follow.unfollowed == False,
                                        Follow.timestamp > d
                                        ).count() + 1

    count = count_as_such + count_to_pump

    if user.user_type == 2:
        if count_to_pump:
            count = int(11*count_to_pump + log(count_to_pump, 2) + sqrt(count_to_pump)) + count_as_such
        else:
            count = count_to_pump + count_as_such

    return count


def get_answer_count(user_id):
    return Post.query.filter(Post.answer_author == user_id,
                             Post.deleted == False
                             ).count()


def get_following_count(user_id):
    return Follow.query.filter(Follow.user == user_id,
                               Follow.unfollowed == False
                               ).count()


def get_users_stats(user_ids, cur_user_id=None):
    print user_ids
    from math import log, sqrt
    from datetime import datetime, timedelta
    trend_time = datetime.now() - timedelta(minutes=5)
    results = db.session.execute(text("""SELECT users.id, users.user_type, users.total_view_count,
                                            (SELECT count(*) FROM user_follows
                                                WHERE user_follows.followed=users.id
                                                    AND user_follows.unfollowed=false
                                                    AND user_follows.timestamp<=:trend_time) AS follow_count_to_pump,

                                            (SELECT count(*) FROM user_follows
                                                WHERE user_follows.followed=users.id
                                                    AND user_follows.unfollowed=false
                                                    AND user_follows.timestamp>:trend_time) AS follow_count_as_such,

                                            (SELECT count(posts.id) FROM posts
                                                WHERE posts.answer_author=users.id
                                                    AND posts.deleted=false) AS answer_count,

                                            (SELECT count(*) FROM user_follows
                                                WHERE user_follows.user=:cur_user_id
                                                    AND user_follows.followed=users.id
                                                    AND user_follows.unfollowed=false) AS is_following,

                                            (SELECT count(questions.id) FROM questions
                                                WHERE questions.question_to=users.id
                                                    AND questions.deleted=false
                                                    AND questions.is_ignored=false
                                                    AND questions.is_answered=false) AS question_count,

                                            (SELECT count(*) FROM profile_requests
                                                WHERE profile_requests.request_for = users.id AND
                                                      profile_requests.request_by = :cur_user_id) AS is_requested

                                    FROM users
                                    WHERE users.id in :user_ids"""),
                                params={'cur_user_id':cur_user_id, 'user_ids':list(user_ids), 'trend_time':trend_time}
                                )
    data = {}
    for row in results:
        follower_count_to_pump = row[3]
        follower_count_as_such = row[4]
        follower_count = follower_count_as_such + follower_count_to_pump
        if row[1] == 2:
            if follower_count_to_pump:
                follower_count = int(11*follower_count_to_pump + log(follower_count_to_pump,2) + sqrt(follower_count_to_pump)) + follower_count_as_such
            else:
                follower_count = follower_count_to_pump + follower_count_as_such

        data[row[0]] = {
                        'following_count':0,
                        'follower_count':follower_count,
                        'view_count':row[2],
                        'answer_count':row[5],
                        'is_following':bool(row[6]),
                        'question_count':row[7],
                        'is_requested': bool(row[8])
                        }

    inflated_stats = InflatedStat.query.filter(InflatedStat.user.in_(user_ids)).all()
    for inflated_stat in inflated_stats:
        data[inflated_stat.user]['follower_count'] += inflated_stat.follower_count
        data[inflated_stat.user]['view_count'] += inflated_stat.view_count

    for post_id, values in data.items():
        if values['view_count'] < values['follower_count']:
            values['view_count'] += values['follower_count'] + 45

    return data


def get_active_mobile_devices(user_id):

    devices = AccessToken.query.filter(AccessToken.user == user_id,
                                       AccessToken.active == True,
                                       AccessToken.push_id != None
                                       ).all()
    return devices


def count_of_push_notifications_sent(user_id):

    result = db.session.execute(text('''Select sum(x.n_count) from (
                                        Select count(*) as n_count from user_push_notifications
                                        where user_id = :user_id and pushed_at >= date_sub(NOW(), interval 1 day)
                                        group by notification_id) as x'''),
                                params={'user_id': user_id})

    for row in result:
        return row[0]


def count_of_notifications_sent_by_type(user_id, notification_type,
                                        interval=datetime.datetime.now() - datetime.timedelta(days=1)):

    result = db.session.execute(text('''Select count(*) from user_push_notifications upn
                                        left join notifications n on n.id = upn.notification_id
                                        where
                                        user_id = :user_id
                                        and n.type = :type_of_notification
                                        and pushed_at >= :interval ;'''),
                                params={"user_id": user_id,
                                         "type_of_notification": notification_type,
                                         "interval": interval})
    for row in result:
        return row[0]
