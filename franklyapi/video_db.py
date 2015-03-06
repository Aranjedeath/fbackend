from models import Video, User, Post, Question, EncodeLog
from app import db, redis_views
from sqlalchemy.sql import text, func
import datetime

def add_video_to_db(video_url, thumbnail_url, video_type, object_id, username=None):
    if not Video.query.filter(Video.url==video_url).count():
        v = Video(url=video_url, thumbnail=thumbnail_url, video_type=video_type, object_id=object_id)
        if username:
            v.username=username
        db.session.add(v)
        db.session.commit()

def add_video_encode_log_start(video_url, video_quality):
    log = EncodeLog(video_url=video_url, video_quality=video_quality, start_time=datetime.datetime.now())
    db.session.add(log)
    db.session.commit()
    return log.id

def update_video_encode_log_finish(encode_log_id,result):
    try:
        success = False
        if result:
            success = True
        else:
            result = False
        EncodeLog.query.filter(EncodeLog.id==encode_log_id).update({'finish_time':datetime.datetime.now(),'success':success})
        db.session.commit()
        
    except Exception as e:
        print e
        db.session.rollback()

def get_encode_statictics(count=100):
    logs = EncodeLog.query.filter().order_by(EncodeLog.start_time.desc()).limit(count).all()
    print len(logs), 'logs found'
    times = []
    fails = 0
    success = 0
    time = 0
    average = 0
    median = 0
    
    for log in logs:
        if log.success :
            success += 1
            times.append((log.finish_time-log.start_time).total_seconds())
        else:
            fails += 1

    if success>0:    
        average = sum(times) / success
        median = get_median(times)
    return {'average':average, 'median':median, 'success':success , 'fails':fails}

def get_median(l):
    half = len(l) / 2
    l.sort()
    if len(l) % 2 == 0:
        return (l[half-1] + l[half]) / 2.0
    else:
        return l[half]

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
        return
        original_url = url
        count = redis_views.get(url)
        
        url = url.replace('http://d35wlof4jnjr70.cloudfront.net/', 'https://s3.amazonaws.com/franklymestorage/')
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
        redis_views.delete(original_url)
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

def get_video_data(video_url):
    video = Video.query.filter(Video.url== video_url).one()

    if video.video_type == 'profile_video':
        user = User.query.filter(User.id==video.object_id).one()
        username = user.username
        answer_author_name = None
        question_author_name = None
        profile_picture = None
        question_body = None

    else:
        post = Post.query.filter(Post.id==video.object_id).one()
        question = Question.query.filter(Question.id==post.question).one()
        question_author = User.query.filter(User.id==post.question_author).one()
        answer_author = User.query.filter(User.id==post.answer_author).one()
        username = answer_author.username
        answer_author_name = answer_author.first_name
        question_author_name = question_author.first_name
        profile_picture = answer_author.profile_picture
        question_body = question.body

    return {
    'video_type':video.video_type,
    'answer_author_username': username,
    'answer_author_name': answer_author_name,
    'question_author_name': question_author_name,
    'question_body':question_body,
    'answer_author_profile_picture': profile_picture
    }




