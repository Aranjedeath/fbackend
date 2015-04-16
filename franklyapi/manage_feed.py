import datetime
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.sql import text

from app import db

from models import User, Post, Question, UserScroll, Upvote, Question
from object_dict import question_to_dict, posts_to_dict, thumb_user_to_dict, questions_to_dict
from configs import config

def get_home_feed(cur_user_id, offset, limit=10, club_questions=True):
    from math import sqrt
    from random import randint

    celebs_following = get_celebs_following(cur_user_id)

    fed_upto_time, fed_upto = get_and_update_fed_marker(cur_user_id, offset)

    print 'fed_upto', fed_upto
    print 'fed_upto_time', fed_upto_time

    # TODO: rewrite query to get feeds after LAST FED MARKER
    posts = db.session.execute(text("""SELECT posts.show_after, posts.id,
                                        posts.question_author, posts.question,
                                        posts.answer_author, posts.media_url,
                                        posts.thumbnail_url, posts.answer_type,
                                        posts.timestamp, posts.deleted, posts.lat,
                                        posts.lon, posts.location_name,
                                        posts.country_name, posts.country_code,
                                        posts.ready, posts.popular,
                                        posts.view_count, posts.client_id
                                        FROM posts INNER JOIN user_follows 
                                        ON user_follows.followed = posts.answer_author
                                            AND user_follows.user = :cur_user_id and user_follows.unfollowed=:unfollowed 
                                        WHERE deleted=false 
                                            AND answer_author != :cur_user_id
                                            AND posts.timestamp <= :fed_upto_time
                                        ORDER BY posts.timestamp DESC,posts.show_after DESC
                                        LIMIT :offset, :limit
                                    """),
                                    params={
                                        'cur_user_id':cur_user_id,
                                        'offset':offset,
                                        'limit':limit,
                                        'unfollowed':False,
                                        'fed_upto_time':fed_upto_time
                                        }
                                )

    posts = list(posts)
    posts = posts_to_dict(posts, cur_user_id)

    shortner = 0
    questions = []
    feeds = []
    _q_len = 0

    question_pages = []
    question_pages_fetched = 0

    if len(celebs_following) > 0:
        while question_pages_fetched < 4:
            # TODO: logic to get question pages from different celebs.
            _q_len, questions, following = get_question_from_followings(celebs_following, cur_user_id=cur_user_id)
            if questions:
                shortner += 1
                question_pages.append((following, questions))
            question_pages_fetched += 1

    if posts:
        print 'posts to hain bhai : ', len(posts)

        # added logic to get count of posts + question pages ----> limit
        if len(posts) + shortner <= limit:
            shortner = 0
        else:
            shortner = len(posts) + shortner - limit

        feeds = [{'type':'post', 'post':post}
                 for post in posts[:len(posts) - shortner]
                 ]

    for question_page in question_pages:
        if club_questions:
            question_user = thumb_user_to_dict(User.query.filter(User.id == question_page[0]).first(), cur_user_id)
            question_user['questions'] = []
            for q in question_page[1]:
                question_user['questions'].append(question_to_dict(q, cur_user_id))
                if len(q.body) > 150:
                    break
                if randint(0, 9) % 2 == 0:
                    break
            idx = randint(0, len(feeds))
            print 'inserting question_page at index : ', idx
            feeds.insert(idx, {'questions': question_user, 'type': 'questions'})
        else:
            questions = []
            for question_page in question_pages:
                questions.append(question_page[1])
            questions = questions_to_dict(questions, cur_user_id)
            for q in questions:
                idx = randint(0, len(feeds))
                print 'inserting question at index : ', idx
                feeds.insert(idx, {'question': q, 'type': 'question'})




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
            print 'user_scroll data created'
        else:
            print 'user_scroll data found'

        post = Post.query.filter(Post.id == UserScroll.fed_upto).first()
        if post:
            fed_upto_time = post.timestamp
        else:
            fed_upto_time = None

        if offset == 0:
            if check_time_threshold_crossed(user_scroll.last_fed,
                config.HOME_FEED_UPDATE_HOURS):
                if check_time_threshold_crossed(user_scroll.last_fed,
                    config.HOME_FEED_UPDATE_LIMIT_REFRESH_HOURS):
                    user_scroll.feed_update_count = 0
                    print 'feed update count reset'
                if user_scroll.feed_update_count < config.HOME_FEED_UPDATE_LIMIT:
                    marker, fed_upto_time = get_updated_feed_marker(
                                                cur_user_id, fed_upto_time
                                                )
                    if marker == None:
                        print 'marker not updated. no rows found.'
                    else:
                        user_scroll.fed_upto = marker
                        user_scroll.feed_update_count += 1
                        print 'feed update count : ', user_scroll.feed_update_count

                user_scroll.last_fed = datetime.datetime.now()
                db.session.commit()
        return fed_upto_time, user_scroll.fed_upto
    else:
        return None, None

def get_updated_feed_marker(cur_user_id, fed_upto_time):
    count = 1
    marker = None
    print 'time aya :', fed_upto_time

    if fed_upto_time:
        result = db.session.execute(text("""SELECT count(*)
                                            FROM posts
                                            INNER JOIN user_follows
                                                ON user_follows.followed = posts.answer_author
                                                   AND user_follows.user = :cur_user_id
                                                   and user_follows.unfollowed=:unfollowed 
                                            WHERE deleted=false AND answer_author != :cur_user_id
                                            AND posts.timestamp > :fed_upto_time
                                        """),
                                    params={
                                        'cur_user_id':cur_user_id,
                                        'unfollowed':False,
                                        'fed_upto_time':fed_upto_time}
                                    )
    else:
        result = db.session.execute(text("""SELECT count(*)
                                            FROM posts
                                            INNER JOIN user_follows
                                                ON user_follows.followed = posts.answer_author
                                                   AND user_follows.user = :cur_user_id
                                                   and user_follows.unfollowed=:unfollowed 
                                            WHERE deleted=false AND answer_author != :cur_user_id
                                        """),
                                    params={
                                        'cur_user_id':cur_user_id,
                                        'unfollowed':False}
                                    )
    for row in result:
        count = row[0]

    offset = max(count/10, 0)
    print 'count: ', count
    print 'shifted marker :', offset, 'places'

    if fed_upto_time:
        result = db.session.execute(text("""SELECT posts.id, posts.timestamp
                                            FROM posts 
                                            INNER JOIN user_follows
                                                ON user_follows.followed = posts.answer_author
                                                   AND user_follows.user = :cur_user_id
                                                   and user_follows.unfollowed=:unfollowed 
                                            WHERE deleted=false AND answer_author != :cur_user_id
                                            AND posts.timestamp > :fed_upto_time
                                            ORDER BY posts.timestamp
                                            Limit :offset, 1
                                        """),
                                    params={
                                        'cur_user_id':cur_user_id,
                                        'unfollowed':False,
                                        'offset':offset,
                                        'fed_upto_time':fed_upto_time}
                                    )
    else:
        result = db.session.execute(text("""SELECT posts.id, posts.timestamp
                                            FROM posts 
                                            INNER JOIN user_follows
                                                ON user_follows.followed = posts.answer_author
                                                   AND user_follows.user = :cur_user_id
                                                   and user_follows.unfollowed=:unfollowed 
                                            WHERE deleted=false AND answer_author != :cur_user_id
                                            ORDER BY posts.timestamp
                                            Limit :offset, 1
                                        """),
                                    params={
                                        'cur_user_id':cur_user_id,
                                        'unfollowed':False,
                                        'offset':offset}
                                    )

    for row in result:
        print row[0]
        marker = row[0]
        fed_upto_time = row[1]

    return marker, fed_upto_time

def check_time_threshold_crossed(last_fed, hours):
    return ((datetime.datetime.now() - last_fed).total_seconds() >
            hours * 3600)
