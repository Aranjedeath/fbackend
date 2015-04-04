import datetime
from sqlalchemy.sql import text

from app import db

from models import User, Post, Question, DiscoverList
from object_dict import questions_to_dict, guest_user_to_dict, posts_to_dict


def get_home_feed(cur_user_id, offset, limit=10):
    from math import sqrt
    from random import randint
  
    celebs_following = get_celebs_following(cur_user_id)

    
    last_fed = get_and_update_fed_marker(cur_user_id, offset)


    # TODO: rewrite query to get feeds after LAST FED MARKER
    posts = db.session.execute(text("""SELECT posts.show_after, posts.id, posts.question_author,
                                        posts.question, posts.answer_author, posts.media_url,
                                        posts.thumbnail_url, posts.answer_type, posts.timestamp,
                                        posts.deleted, posts.lat, posts.lon, posts.location_name,
                                        posts.country_name, posts.country_code, posts.ready,
                                        posts.popular, posts.view_count, posts.client_id
                                        FROM posts INNER JOIN user_follows ON user_follows.followed = posts.answer_author
                                        AND user_follows.user = :cur_user_id and user_follows.unfollowed=:unfollowed 
                                        #AND timestampdiff(minute, user_follows.timestamp, now()) >= posts.show_after 
                                        WHERE deleted=false AND answer_author != :cur_user_id
                                        AND posts.timestamp > :last_fed

                                        ORDER BY posts.timestamp DESC,posts.show_after DESC LIMIT :offset, :limit"""),
                                    params = {'cur_user_id':cur_user_id, 'offset':offset, 'limit':limit, 'unfollowed':False, 'last_fed':user_scroll.last_fed}
                                )

    posts = list(posts)
    posts = posts_to_dict(posts, cur_user_id)

    
    shortner = 0
    questions = []
    feeds = []
    _q_len = 0
    if len(celebs_following) > 0:
        _q_len, questions, following = get_question_from_followings(celebs_following, cur_user_id=cur_user_id)
        if questions:
            shortner = 1

    if posts:
        feeds = [{'type':'post', 'post':post} for post in posts[:len(posts) - shortner]]

    if questions:
        question_user = thumb_user_to_dict(User.query.filter(User.id == following).first(), cur_user_id)
        question_user['questions'] = []
        for q in questions:
            question_user['questions'].append(question_to_dict(q, cur_user_id))
            if len(q.body) > 150:
                break
            if randint(0,9) % 2 == 0:
                break
        if posts:
            idx = randint(0,len(posts)- 1)
        else:
            idx = 0
        feeds.insert(idx, {'questions': question_user, 'type' : 'questions'} )

    tentative_idx = -1
    if int(len(celebs_following) * sqrt(_q_len)): 
        tentative_idx = offset + limit + int(len(celebs_following) * sqrt(_q_len))

    # TODO: limit must be replaced by len(posts)
    next_index = offset+limit-shortner if posts else tentative_idx if offset < 40 else -1

    return feeds, next_index    

def get_question_from_followings(followings, count = 2, cur_user_id=None):
    from random import choice
    following = choice(followings)[0]
    user = User.query.filter(User.id == following).first()
    
    questions_query = Question.query.filter(Question.question_to==following, 
                                            Question.question_author!=cur_user_id,
                                            Question.deleted==False,
                                            Question.is_answered==False,
                                            Question.is_ignored==False
                                            ).outerjoin(Upvote
                                            ).group_by(Question.id
                                            ).order_by(Question.score.desc()
                                            ).order_by(func.count(Upvote.id).desc()
                                            ).limit(40)
    questions = questions_query.all()
    _q_len = len(questions)
    if _q_len < 2:
        return _q_len, [], following
    else:
        q1, q2 = choice(questions), choice(questions)
        while q1 == q2:
            q2 = choice(questions)
        return _q_len, [q1, q2], following

def get_celebs_following(cur_user_id):
    return db.session.execute(
        text("""SELECT followed from user_follows
                left join users on user_follows.followed = users.id 
                where user_follows.user = :cur_user_id and user_follows.unfollowed = :unfollowed and users.user_type = 2"""),
        params={'cur_user_id':cur_user_id, 'unfollowed':False}
        ).fetchall()

def get_and_update_fed_marker(cur_user_id, offset):
    if cur_user_id:
        user_scroll = UserScroll.query.filter(
            UserScroll.user == cur_user_id).first()
        if not user_scroll:
            user_scroll = UserScroll(cur_user_id)
            db.session.add(user_scroll)
            db.session.commit()

        if offset == 0:
            if check_time_threshold_crossed(user_scroll.last_fed,config.HOME_FEED_UPDATE_HOURS):
                if check_time_threshold_crossed(user_scroll.last_fed,config.HOME_FEED_UPDATE_LIMIT_REFRESH_HOURS):
                    user_scroll.feed_update_count = 0
                if user_scroll.feed_update_count >= config.HOME_FEED_UPDATE_LIMIT:
                    user_scroll.fed_upto = get_updated_feed_marker()
                    user_scroll.feed_update_count += 1

                user_scroll.last_fed = datetime.datetime.now()
                db.session.commit()
        return user_scroll.last_fed
    else:
        return None

def get_updated_feed_marker(cur_user_id):
    count = 1
    result = db.session.execute(text("""SELECT count(*)
                                        FROM posts 
                                        INNER JOIN user_follows
                                            ON user_follows.followed = posts.answer_author
                                               AND user_follows.user = :cur_user_id
                                               and user_follows.unfollowed=:unfollowed 
                                               # AND timestampdiff(minute, user_follows.timestamp, now()) >= posts.show_after 
                                        WHERE deleted=false AND answer_author != :cur_user_id
                                        and (select count(*) from )
                                        ORDER BY
                                            posts.timestamp 
                                    """),
                                params = {
                                    'cur_user_id':cur_user_id,
                                    'unfollowed':False}
                                )
    for row in result:
        count = row[0]

    offset = max(count/10,1)

    result = db.session.execute(text("""SELECT posts.timestamp
                                        FROM posts 
                                        INNER JOIN user_follows
                                            ON user_follows.followed = posts.answer_author
                                               AND user_follows.user = :cur_user_id
                                               and user_follows.unfollowed=:unfollowed 
                                               # AND timestampdiff(minute, user_follows.timestamp, now()) >= posts.show_after 
                                        WHERE deleted=false AND answer_author != :cur_user_id
                                        and (select count(*) from )
                                        ORDER BY
                                            posts.timestamp 
                                        Limit :offset, 1
                                    """),
                                params = {
                                    'cur_user_id':cur_user_id,
                                    'unfollowed':False,
                                    'offset':offset}
                                )
    for row in result:
        marker = row[0]

    return marker

def check_user_last_fed_threshold_cross(last_fed):
    return ((datetime.datetime.now() - last_fed).total_seconds() >
            config.HOME_FEED_UPDATE_HOURS * 3600)