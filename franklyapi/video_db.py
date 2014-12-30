from models import Video
from app import db, redis_data_client
from sqlalchemy.sql import text

def add_video_to_db(video_url, thumbnail_url=None):
    if not Video.query.filter(Video.url==video_url).count():
        db.session.add(Video(url=video_url, thumbnail=thumbnail_url))
        db.session.commit()


def update_video_state(video_url, result={}):
    if result:
        print result
        result.update({'process_state':'success'})
        Video.query.filter(Video.url==video_url).update(result)
    else:
        Video.query.filter(Video.url==video_url).update({'process_state':'failed'})
        db.session.commit()


def update_view_count_to_db(url):
    url = url.replace('http://d35wlof4jnjr70.cloudfront.net/', 'https://s3.amazonaws.com/franklyapp/')
    count = redis_data_client.get(url)
    if count:
        db.session.execute(text("""UPDATE users 
                                    SET view_count=view_count+:count 
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
    redis_data_client.delete(url)
