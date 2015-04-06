from models import Question, Upvote, InflatedStat, User, Follow, Like

def get_post_like_count(post_id):
    count = Like.query.filter(Like.post==post_id, Like.unliked==False).count()
    return count

def get_question_upvote_count(question_id):
    from math import sqrt, log
    from datetime import datetime, timedelta
    d = datetime.now() - timedelta(minutes = 5)
    question = Question.query.filter(Question.id == question_id).first()
    t = question.timestamp
    time_factor = 0
    if t:
        time_factor = int(time.mktime(t.timetuple())) % 7
    count_to_pump = Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False, Upvote.timestamp <= d).count()
    count_as_such = Upvote.query.filter(Upvote.question==question_id, Upvote.downvoted==False, Upvote.timestamp > d).count()
    if count_to_pump:
        count = int(11*count_to_pump+ log(count_to_pump, 2) + sqrt(count_to_pump)) + count_as_such
        count += time_factor
    else:
        count = count_to_pump + count_as_such
    inflated_stat = InflatedStat.query.filter(InflatedStat.question==question_id).first()
    if inflated_stat:
        count += inflated_stat.upvote_count
    return count


def get_follower_count(user_id):
    from math import log, sqrt
    from datetime import datetime, timedelta
    user = User.query.filter(User.id==user_id).one()

    d = datetime.now() - timedelta(minutes = 5)
    count_to_pump =  Follow.query.filter(Follow.followed==user_id, Follow.unfollowed==False, Follow.timestamp <= d).count()
    count_as_such = Follow.query.filter(Follow.followed==user_id, Follow.unfollowed==False, Follow.timestamp > d).count() +1
    count = count_as_such + count_to_pump

    if user.user_type == 2:
        if count_to_pump:
            count = int(11*count_to_pump + log(count_to_pump,2) + sqrt(count_to_pump)) + count_as_such
        else:
            count = count_to_pump + count_as_such

    return count