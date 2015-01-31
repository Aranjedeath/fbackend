from models import Video, User
from app import db, redis_data_client
from sqlalchemy.sql import text, func

def add_video_to_db(video_url, thumbnail_url, video_type, object_id, username=None):
    if not Video.query.filter(Video.url==video_url).count():
        v = Video(url=video_url, thumbnail=thumbnail_url, video_type=video_type, object_id=object_id)
        if username:
            v.username=username
        db.session.add(v)
        db.session.commit()


def update_video_state(video_url, result={}):
    try:
        if result:
            print result
            result.update({'process_state':'success'})
            Video.query.filter(Video.url==video_url).update(result)
            db.session.commit()
        else:
            Video.query.filter(Video.url==video_url).update({'process_state':'failed'})
            db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()


def update_view_count_to_db(url):
    try:
        original_url = url
        count = redis_data_client.get(url)
        
        url = url.replace('http://d35wlof4jnjr70.cloudfront.net/', 'https://s3.amazonaws.com/franklyapp/')
        types = ['_ultralow', '_low', '_medium', '_opt', '_promo']
        for suffix in types:
            url = url.replace(suffix, '')
        
        if count:
            db.session.execute(text("""UPDATE users 
                                        SET view_count=view_count+:count, total_view_count=total_view_count+:count
                                        WHERE profile_video=:url
                                    """),
                                params = {"url":url, "count":int(count)}
                            )
            db.session.execute(text("""UPDATE posts 
                                        SET view_count=view_count+:count 
                                        WHERE media_url=:url
                                    """),
                                params = {"url":url, "count":int(count)}
                            )
            db.session.commit()
        redis_data_client.delete(original_url)
    except:
        db.session.rollback()

def update_total_view_count(user_ids): 
    try:   
        result = db.session.execute(text("""SELECT answer_author, sum(posts.view_count)
                                        AS post_views 
                                        FROM posts 
                                        WHERE posts.answer_author in :user_ids"""
                                        ),
                                    params={'user_ids':user_ids}
                                    )
        result = dict(list(result))
        
        for user_id, post_view_count in result.items():
            if not post_view_count:
                post_view_count = 0
            
            db.session.execute(text("""UPDATE users 
                                        SET total_view_count=view_count+:post_view_count
                                        WHERE id=:user_id"""
                                ), params={'user_id':user_id, 'post_view_count':int(post_view_count)})

        db.session.commit()
    except:
        db.session.rollback()

