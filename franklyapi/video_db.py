from models import Video
from app import db

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
