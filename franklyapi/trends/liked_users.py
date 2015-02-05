from app import db
from sqlalchemy.sql import text

def most_liked_users(current_user_id=None):
    current_user_clause = ''
    if current_user_id:
        if type(current_user_id) == type([]):
            current_user_clause = " post_likes.user in :current_user_id "
        elif type(current_user_id) == type(''):
            current_user_clause = " post_likes.user=:current_user_id "

    results = db.session.execute(text("""SELECT posts.answer_author, count(posts.id) AS like_count 
                            FROM post_likes JOIN posts ON post_likes.post=posts.id AND {current_user_clause}
                            GROUP BY posts.answer_author 
                            ORDER BY like_count DESC""".format(current_user_clause=current_user_clause)),
                        params = {'current_user_id':current_user_id}
                    )

    user_ids = [(row(0), row(1)) for row in results]
    return user_ids

def most_likes_users_trending(timefrom, current_user_id=None):
    import datetime

    current_user_clause = ''
    if current_user_id:
        if type(current_user_id) == type([]):
            current_user_clause = " post_likes.user in :current_user_id "
        elif type(current_user_id) == type(''):
            current_user_clause = " post_likes.user=:current_user_id "

    results = db.session.execute(text("""SELECT posts.answer_author, count(posts.id) AS like_count 
                                        FROM post_likes JOIN posts ON post_likes.post=posts.id AND {current_user_clause}
                                        WHERE post_likes.timestamp > :from_datetime
                                        GROUP BY posts.answer_author 
                                        ORDER BY like_count DESC""".format(current_user_clause=current_user_clause)),
                            params = {'current_user_id':current_user_id,
                                    'from_datetime':datetime.datetime.now()-datetime.timedelta(seconds=timefrom)}
                    )

    user_ids = [(row(0), row(1)) for row in results]
    return user_ids