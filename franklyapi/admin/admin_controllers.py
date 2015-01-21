from models import *
from object_dict import *
from app import db
import controllers
import random
import media_uploader
import async_encoder
import video_db

def user_list(user_type, deleted, offset, limit, order_by, desc):
    user_query = User.query.filter(User.user_type==user_type, User.deleted==deleted)

    if order_by == 'user_since':
        order = User.user_since if not desc else User.user_since.desc()

    elif order_by == 'name':
        order = User.first_name if not desc else User.first_name.desc()

    users = user_query.order_by(order).offset(offset).limit(limit).all()
    users = [user_to_dict(user) for user in users]

    next_index = -1 if len(users)<limit else offset+limit

    return {'next_index':next_index, 'users':users, 'count':len(users), 'offset':offset, 'limit':limit}

def get_random_fake_user(gender=None):
    user_query = User.query.filter(User.user_type==-1)
    if gender:
        user_query.filter(User.gender==gender)

    count = user_query.count()
    offset = random.randint(0,count-1)
    return user_query.offset(offset).limit(1)[0].id



def user_add(email, username, first_name, bio, password, user_title, user_type, profile_picture, profile_video, gender):
    resp = controllers.register_email_user(email, password, first_name, device_id='web', username=username, phone_num=None,
                                    gender=gender, user_type=user_type, user_title=user_title, 
                                    bio=bio, profile_picture=profile_picture, profile_video=profile_video, admin_upload=True)

    return {'success':True, 'user':user_to_dict(User.query.get(resp['id']))}


def user_edit(user_id, email, username, first_name, bio, password, user_title, user_type, profile_picture, profile_video, deleted=False, phone_num=None):
    if username:
        controllers.user_change_username(user_id, username)
    if password:
        controllers.user_change_password(user_id, password)

    if deleted:
        User.query.filter(User.id==user_id).update({'deleted':deleted})

    controllers.user_update_profile_form(user_id, first_name=first_name, 
                                        bio=bio,
                                        profile_picture=profile_picture,
                                        profile_video=profile_video,
                                        user_type=user_type,
                                        phone_num=phone_num,
                                        admin_upload=True,
                                        user_title=user_title,
                                        email=email)

    db.session.commit()
    return {'success':True, 'user':user_to_dict(User.query.get(user_id))}

def post_list(offset, limit, deleted, order_by, desc, celeb=True, answer_authors=[], question_authors=[]):
    post_query = Post.query.filter(Post.deleted==deleted)

    if celeb:
        post_query.join((User, Post.answer_author==User.id)).filter(User.user_type==2)

    if answer_authors:
        post_query.filter(Post.answer_author.in_(answer_authors))
    if question_authors:
        post_query.filter(Post.question_author.in_(question_authors))

    if order_by == 'timestamp':
        order = Post.timestamp if not desc else Post.timestamp.desc()

    posts = post_query.order_by(order).offset(offset).limit(limit).all()
    posts = posts_to_dict(posts)

    next_index = -1 if len(posts)<limit else offset+limit

    return {'next_index':next_index, 'posts':users, 'count':len(posts), 'offset':offset, 'limit':limit}

def post_add(question_id, video, answer_type='video'):
    from random import choice
    answer_author = Question.query.get(question_id).question_to
    show_after = db.session.execute('Select max(show_after) from posts where answer_author = %s'%answer_author).first()
    if show_after:
        show_after = show_after[0] + choice([360,720, 1080 ])
    return controllers.add_video_post(answer_author, question_id, video, answer_type,
                        lat=None, lon=None, show_after = show_after)

def post_unanswer(post_id):
    post = Post.query.filter(Post.id==post_id).one()
    question_id = post.question
    Question.query.filter(Question.id==question_id).update({'is_answered':False})
    Post.query.filter(Post.id==post_id).delete()
    db.session.commit()
    return {'success':True}

def post_edit(post_id, video, answer_type='video'):
    answer_author = Question.query.get(question_id).question_to
    video_url, thumbnail_url = media_uploader.upload_user_video(user_id=answer_author, video_file=video, video_type='answer')
    
    Post.query.filter(Post.id==post_id).update({'media_url':video_url, 'thumbnail_url':thumbnail_url})
    db.session.commit()

    curruser = User.query.filter(User.id == answer_author).one()

    video_db.add_video_to_db(video_url, thumbnail_url)
    async_encoder.encode_video_task.delay(video_url, curruser.username)
    
    return {'success': True, 'id':post_id}


def question_list(offset, limit, user_to=[], user_from=[], public=True, deleted=False):
    questions = Question.query.filter(Question.deleted==deleted, Question.public==public, Question.is_answered==False, Question.is_ignored==False
                                    ).order_by(Question.timestamp.desc()
                                    ).offset(offset
                                    ).limit(limit
                                    ).all()
    return {'questions': [question_to_dict(question) for question in questions], 'next_index':offset+limit}


def question_add(question_to, body, question_author=None, is_anonymous=False, score=500, question_author_gender=None):
    if not question_author:
        from random import choice
        question_author = choice([u'481bc87c43bc4812b0e333ecd9cd4c2c',
                                 u'eead306ebd2a4e8b8b740c2b9462c250',
                                 u'cab4132c5445437ddf31032339d5882f',
                                 u'cab4132c53c79664df310373dba392db',
                                 u'cab4132c53df5eafdf31034108378042',
                                 u'd8ace0a534c041bc91ccef22c399f73e',
                                 u'cab4132c540dba153aac284093d3fcca',
                                 u'cab4132c53c6a513df310374a482ef4e',
                                 u'cab4132c53c6af3edf310377b4a32d13',
                                 u'cab4132c53c6a447df3103743a3fabdf'])
        #question_author = get_random_fake_user(gender=question_author_gender)
    return controllers.question_ask(question_author, question_to=question_to, body=body, is_anonymous=is_anonymous, lat = 0.0, lon=0.0)


def question_delete(question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':True})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def question_undelete(question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':False})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def question_edit(question_id, body):
    Question.query.filter(Question.id==question_id).update({'body':body.capitalize()})
    db.session.commit()
    return {'success':True, 'question_id':question_id}
 
def get_que_order(offset = 0, limit =10 ):
    queue = CentralQueueMobile.query.all()
    result = []
    for item in queue:
        if item.user:
            user = User.query.filter(User.id == item.user).first()
            user = search_user_to_dict(user)
            result.append(
                {
                    'type' : 'user',
                    'id' : item.id,
                    'day' : item.day,
                    'score' : item.score,
                    'user' : user
                }
            )
    result = sorted(result, key=lambda x:x['day'], reverse = True)
        #Write code for posts and questions
    return {
        'results' : result
        }

def update_que_order(_id, day, score):
    item = CentralQueueMobile.query.filter(CentralQueueMobile.id == _id).first()
    if not item:
        return {'success' : False,'message' : 'wrong id provided'}
    item.day = day
    item.score = score
    db.session.add(item)
    db.session.commit()
    return {'success' : True}

def get_celeb_list(offset = 0, limit = 10):
    celebs = db.session.execute('select users.id, users.username, users.first_name, users.profile_picture, users.user_type, users.user_title, central_queue_mobile.user, central_queue_mobile.day, central_queue_mobile.score from users left join central_queue_mobile on users.id = central_queue_mobile.user where users.user_type = 2 limit %s,%s'%(offset,limit))
    results = []
    for celeb in celebs:
        user = search_user_to_dict(celeb)
        user['in_list'] = True if celeb.user else False
        user['day'] = celeb.day
        user['score'] = celeb.score
        results.append(user)
    results = sorted(results, key=lambda x:x['day'], reverse = True)
    return {'results' : results}

def add_celeb_in_queue(item_id, item_type, item_day, item_score):
    type_dict = {
            'user' : CentralQueueMobile.user,
            'post' : CentralQueueMobile.post,
            'question' : CentralQueueMobile.question
        }
    que_entry = CentralQueueMobile.query.filter(type_dict[item_type] == item_id).first()
    if not que_entry:
        que_entry = CentralQueueMobile(item_type, item_id)
    que_entry.day = item_day
    que_entry.score = item_score
    db.session.add(que_entry)
    db.session.commit()
    return {'success' : True}


