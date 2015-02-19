from models import *
from object_dict import *
from app import db
import controllers
import random
import media_uploader
import async_encoder
import video_db
from sqlalchemy import or_, text
import time
import datetime


def get_user_activity_timeline(user_id, start_time=0, end_time=99999999999):
    user = User.query.filter(User.id==user_id).one()
    
    profile_edits = UserArchive.query.filter(UserArchive.user==user_id,
                                            UserArchive.timestamp>=datetime.datetime.fromtimestamp(start_time),
                                            UserArchive.timestamp<datetime.datetime.fromtimestamp(end_time),
                                            ).order_by(UserArchive.timestamp.desc()
                                            ).all()
    posts = Post.query.filter(Post.answer_author==user_id,
                                Post.timestamp>=datetime.datetime.fromtimestamp(start_time),
                                Post.timestamp<datetime.datetime.fromtimestamp(end_time),
                            ).order_by(Post.timestamp.desc()
                            ).all()

    resp = defaultdict(list)
    resp[maketimestamp(user.user_since)].append({   
                                                'action':'account_created',
                                                'action_by':user.added_by
                                                })               

    previous_item = UserArchive(user=user_id, username=None, first_name=None,
                                profile_picture=None, profile_video=None,
                                cover_picture=None, bio=None, user_title=None)
    
    for item in profile_edits:
        if item.profile_video and item.profile_video!=previous_item.profile_video:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'profile_video_changed',
                                                        'action_by':item.moderated_by
                                                        })
        if item.profile_picture and item.profile_picture!=previous_item.profile_picture:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'profile_video_changed',
                                                        'action_by':item.moderated_by
                                                        })
        if item.username and item.username!=previous_item.username:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'username_changed',
                                                        'action_by':item.moderated_by
                                                        })
        if item.first_name and item.first_name!=previous_item.first_name:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'name_changed',
                                                        'action_by':item.moderated_by
                                                        })
        if item.bio and item.bio!=previous_item.bio:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'bio_changed',
                                                        'action_by':item.moderated_by
                                                        })
        if item.user_title and item.user_title!=previous_item.user_title:
            resp[maketimestamp(item.timestamp)].append({   
                                                        'action':'user_title_changed',
                                                        'action_by':item.moderated_by
                                                        })
        previous_item = item

    for post in posts:
        resp[maketimestamp(post.timestamp)].append({'action':'post_added',
                                                    'action_by':post.added_by,
                                                    'edited_by':post.moderated_by,
                                                    'web_link':'http://frankly.me/p/{client_id}'.format(client_id=post.client_id)
                                                    })

    timeline = [{'timestamp':item, 'actions':actions} for timestamp, actions in resp.items()]
    timeline.sort(key=lambda x: x['timestamp'], reverse=True)
    return {'user':thumb_user_to_dict(user), 'start_time':start_time, 'end_time':end_time, 'timeline':timeline}




def user_list(user_type, deleted, offset, limit, order_by, desc, since_time):
    user_query = User.query.filter(User.user_type==user_type, User.deleted==deleted,User.user_since >= since_time)

    if order_by == 'user_since':
        order = User.user_since if not desc else User.user_since.desc()

    elif order_by == 'name':
        order = User.first_name if not desc else User.first_name.desc()

    users = user_query.order_by(order).offset(offset).limit(limit).all()
    users = [user_to_dict(user) for user in users]

    next_index = -1 if len(users)<limit else offset+limit

    return {'next_index':next_index, 'users':users, 'count':len(users), 'offset':offset, 'limit':limit}


def get_random_fake_user(gender=None):
    fake_users = ["harmanRathore", "vivek_verma", "pooja_verma", "minal_singh", "vikrant_thapar", "Anthony_Gonzales", "Pravin_Parvani", "ridhi_kalra", "manoj_singh", "neetu_gupta"]
    genders = ['M', 'F', None]
    
    if gender:
        genders = [gender]
    
    user_query = User.query.filter(User.username.in_(fake_users), User.gender.in_(genders))
    count = user_query.count()
    offset = random.randint(0,count-1)
    user = user_query.offset(offset).limit(1)[0]
    return user.id



def user_add(current_user_id, email, username, first_name, bio, password, user_title, user_type, profile_picture, profile_video, gender):
    
    resp = controllers.register_email_user(email, password, first_name, device_id='web',
                                            username=username, phone_num=None, gender=gender,
                                            user_type=user_type, user_title=user_title, bio=bio,
                                            profile_picture=profile_picture, profile_video=profile_video, 
                                            admin_upload=True, added_by=current_user_id)
    
    db.session.commit()
    
    return {'success':True, 'user':user_to_dict(User.query.get(resp['id']))}


def user_edit(current_user_id, user_id, email, username, first_name, bio, 
                password, user_title, user_type, profile_picture, profile_video,
                deleted=False, phone_num=None):
    if username:
        controllers.user_change_username(user_id, username)
    if password:
        controllers.user_change_password(user_id, password)

    if deleted:
        User.query.filter(User.id==user_id).update({'deleted':deleted})

    controllers.user_update_profile_form(   
                                            user_id,
                                            first_name=first_name, 
                                            bio=bio,
                                            profile_picture=profile_picture,
                                            profile_video=profile_video,
                                            user_type=user_type,
                                            phone_num=phone_num,
                                            admin_upload=True,
                                            user_title=user_title,
                                            email=email,
                                            moderated_by=current_user_id
                                        )
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



def post_add(current_user_id, question_id, video, answer_type='video'):
    from random import choice
    answer_author = Question.query.with_entities('answer_author').get(question_id).question_to

    show_after = db.session.execute(text("""SELECT max(show_after) 
                                                FROM posts 
                                                WHERE answer_author=:answer_author"""),
                                    params={'answer_author':answer_author}).first()
    
    show_after = show_after[0] + choice([360,720, 1080 ]) if show_after else None
    
    resp = controllers.add_video_post(cur_user_id=answer_author, question_id=question_id, 
                                        video=video, answer_type=answer_type,
                                        lat=None, lon=None, show_after = show_after, added_by=current_user_id)
    db.session.commit()
    return resp


def post_edit(current_user_id, post_id, video, answer_type='video'):
    post = Post.query.filter(Post.id==post_id).first()
    video_url, thumbnail_url = media_uploader.upload_user_video(user_id=post.answer_author, video_file=video, video_type='answer')
    Post.query.filter(Post.id==post_id).update({'media_url':video_url, 'thumbnail_url':thumbnail_url, 'moderated_by':current_user_id})

    username = User.query.with_entities('username').filter(User.id==post.answer_author).one().username

    video_db.add_video_to_db(video_url, thumbnail_url, 'answer_video', post_id, username)
    async_encoder.encode_video_task.delay(video_url, username)
    
    db.session.commit()

    return {'success': True, 'id':post_id}


def question_list(offset, limit, user_to=[], user_from=[], public=True, deleted=False):
    questions = Question.query.filter(Question.deleted==deleted, Question.public==public, Question.is_answered==False, Question.is_ignored==False
                                    ).order_by(Question.timestamp.desc()
                                    ).offset(offset
                                    ).limit(limit
                                    ).all()
    return {'questions': [question_to_dict(question) for question in questions], 'next_index':offset+limit}


def question_add(current_user_id, question_to, body, question_author=None, is_anonymous=False, score=500, question_author_gender=None):
    question_author = get_random_fake_user(gender=question_author_gender) if not question_author else question_author
    resp = controllers.question_ask(question_author, 
                                    question_to=question_to,
                                    body=body, 
                                    is_anonymous=is_anonymous,
                                    lat = 0.0,
                                    lon=0.0,
                                    added_by=current_user_id)
    db.session.commit()
    return resp


def question_delete(current_user_id, question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':True, 'moderated_by':current_user_id})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def question_undelete(current_user_id, question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':False, 'moderated_by':current_user_id})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def question_edit(current_user_id, question_id, body, slug=None):
    update_dict = {'body':body.capitalize(), 'moderated_by':current_user_id}
    if slug:
        slug = slugify.slugify(unicode(slug))
        update_dict.update({'slug':slug})
    Question.query.filter(Question.id==question_id).update(update_dict)
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def question_redirect(question_ids, redirect_to):
    Question.query.filter(Question.id.in_(question_ids)).update(Question.redirect_to == redirect_to)
    db.session.commit() 
    return {'success':True}



def question_change_upvotes(question_id, change_count):
    if change_count < 0:
        return question_decrease_upvotes(question_id, change_count*-1)
    if change_count > 0:
        return question_increase_upvotes(question_id, change_count)


def question_increase_upvotes(question_id, count):
    from controllers import question_upvote
    results = db.session.execute(text("""SELECT users.id FROM users JOIN question_upvotes 
                                                    ON users.id=question_upvotes.user
                                                WHERE users.monkness in :monkness
                                                    AND question_upvotes.downvoted=false"""),
                                params = {'monkness':[1, 0]}
                                )

    for user in User.query.with_entities('id').filter(  User.monkness.in_([1, 0]),
                                                        ~User.id.in_([row[0] for row in results])
                                                    ).limit(count/10).all():

        resp = question_upvote(user.id, question_id)

    return {'count': count}

def question_decrease_upvotes(question_id, count):
    from controllers import question_downvote
    results = db.session.execute(text("""SELECT users.id FROM users JOIN question_upvotes 
                                                    ON users.id=question_upvotes.user
                                                WHERE users.monkness in :monkness
                                                    AND question_upvotes.downvoted=false
                                                ORDER BY question_upvotes.timestamp DESC
                                                LIMIT 0, :count
                                                """),
                                params = {'monkness':[1, 0], 'count':count}
                                )
    for row in results:
        question_downvote(row[0], question_id)

    return {'count':count}


def get_search_words(question_body):
    stop_words = ["i" , "me" , "my" , "myself" , "we" , "our" , "ours" , "ourselves" ,
                    "you" , "your" , "yours" , "yourself" , "yourselves" , "he" , "him" ,
                    "his" , "himself" , "she" , "her" , "hers" , "herself" , "it" , "its" ,
                    "itself" , "they" , "them" , "their" , "theirs" , "themselves" , "what" ,
                    "which" , "who" , "whom" , "this" , "that" , "these" , "those" , "am" ,
                    "is" , "are" , "was" , "were" , "be" , "been" , "being" , "have" , "has" ,
                    "had" , "having" , "do" , "does" , "did" , "doing" , "a" , "an" , "the" ,
                    "and" , "but" , "if" , "or" , "because" , "as" , "until" , "while" , "of" ,
                    "at" , "by" , "for" , "with" , "about" , "against" , "between" , "into" ,
                    "through" , "during" , "before" , "after" , "above" , "below" , "to" ,
                    "from" , "up" , "down" , "in" , "out" , "on" , "off" , "over" , "under" ,
                    "again" , "further" , "then" , "once" , "here" , "there" , "when" , "where" ,
                    "why" , "how" , "all" , "any" , "both" , "each" , "few" , "more" , "most" ,
                    "other" , "some" , "such" , "no" , "nor" , "not" , "only" , "own" , "same" ,
                    "so" , "than" , "too" , "very" , "s" , "t" , "can" , "will" , "just" ,
                    "don" , "should" , "now"
                ]
    search_words = filter(lambda x:x, map(lambda x:x.strip() if x not in stop_words else False, question_body.split(' ')))
    return search_words

def get_similar_questions(question_id):
    question = Question.query.filter(Question.id == question_id).first()
    search_words = get_search_words(question.body)
    questions = Question.query.filter(Question.question_to == question.question_to, Question.id != question.id, Question.body.op('regexp')('|'.join(search_words))).all()
    result = {'questions' : [question_to_dict(q) for q in questions[0:10]], 'question_id' : question_id}
    print result
    return result

def get_unanswered_questions_with_same_count(user_id, offset, limit):
    questions = Question.query.filter(Question.question_to == user_id, Question.is_answered == False).offset(offset).limit(limit).all()
    print questions
    res = []
    for question in questions:
        search_words = get_search_words(question.body)
        print search_words
        count = Question.query.filter(Question.question_to == question.question_to, Question.id != question.id, Question.body.op('regexp')('|'.join(search_words))).count()
        question_dict = question_to_dict(question)
        question_dict['similar_questions'] = count
        res.append(question_dict)
    next_index = offset + limit if len(res) == limit else -1
    return {'questions' : res, 'count' : len(res), 'next_index' : next_index}

def update_category_order_search_default(category_name, user_cat_data):
    '''
    user_cat_data example : {
                                'user_id' : string user id,
                                'score' : integer score
                            }
    '''
    cat_users_count = SearchDefault.query.filter(SearchDefault.category == category_name).count()
    if not cat_users_count:
        return {'success': False, 'message': 'cannot add categories abhi!!!'}
    for user_data in user_cat_data:
        s = SearchDefault.query.filter(SearchDefault.user == user_data['user_id'], SearchDefault.category == category_name).first()
        if not s:
            s = SearchDefault(user = user_data['user_id'],
                              category = category_name)
        s.score = user_data['score']
        db.session.add(s)
        db.session.commit()
    return {'success':True}

def delete_search_default_user(category_name, user_id):
    s = SearchDefault.query.filter(SearchDefault.user == user_id, SearchDefault.category == category_name).delete()
    db.session.commit()
    return {'success' : True}
        
def get_que_order(offset = 0, limit =10 ):
    queue = CentralQueueMobile.query.order_by(CentralQueueMobile.score).all()
    result = []
    for item in queue:
        if item.user:
            user = User.query.filter(User.id == item.user).first()
            user = thumb_user_to_dict(user)
            result.append(
                {
                    'type' : 'user',
                    'id' : item.id,
                    'day' : item.day,
                    'score' : item.score,
                    'user' : user
                }
            )
        if item.post:
            post = Post.query.filter(Post.id == item.post).first()
            post = post_to_dict(post)
            result.append(
                {
                    'type' : 'post',
                    'id' : item.id,
                    'day' : item.day,
                    'score' : item.score,
                    'post' : post
                }
            )
    return {
        'results' : result
        }

def update_que_order(items):
    type_dict = {
            'user' : CentralQueueMobile.user,
            'post' : CentralQueueMobile.post,
            'question' : CentralQueueMobile.question
        }
    for item in items:
        que_entry = CentralQueueMobile.query.filter(type_dict[item['type']] == item['id']).first()
        if not que_entry:
            que_entry = CentralQueueMobile(item['type'], item['id'])
        que_entry.score = item['score']
        db.session.add(que_entry)
    db.session.commit()
    return {'success' : True}

def get_celeb_list(since_time,offset = 0, limit = 10):
    #celebs = db.session.execute('select users.id, users.username, users.deleted, users.first_name, users.profile_picture, users.user_type, users.user_title, central_queue_mobile.user, central_queue_mobile.day, central_queue_mobile.score from users left join central_queue_mobile on users.id = central_queue_mobile.user where users.user_type = 2 and user_since : limit %s,%s'%(offset,limit))
    
    celebs = db.session.execute(text("""SELECT users.id, users.username, users.deleted, users.first_name, users.profile_picture, users.user_type, users.user_title, central_queue_mobile.user, central_queue_mobile.day, central_queue_mobile.score 
                                            from users 
                                            left join central_queue_mobile 
                                            on users.id = central_queue_mobile.user 
                                            where users.user_type = 2 
                                                and users.user_since > :since_time 
                                            limit :offset,:limit"""),
                                params={'since_time':since_time, 'limit':limit, 'offset':offset}
                                )
    results = []
    for celeb in celebs:
        user = thumb_user_to_dict(celeb)
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

def maketimestamp(datetime_obj):
    if not datetime_obj:
        return None
    else:
        return int(time.mktime(datetime_obj.timetuple()))

def get_celeb_search(query):
    search_filter = or_(  User.username.like('{query}%'.format(query=query)),
                                    User.first_name.like('% {query}%'.format(query=query)),
                                    User.first_name.like('{query}%'.format(query=query))
                               )
    results = []
    users = User.query.filter(search_filter, User.user_type == 2).all()
    user_ids = []
    post_ids = []
    for user in users:
        results.append({'type':'user', 'user':thumb_user_to_dict(user)})
        user_ids.append(user.id)
    posts = Post.query.filter(Post.answer_author.in_(map(lambda x:x.id,users))).all()
    for post in posts:
        results.append({'type':'post', 'post':post_to_dict(post)})
        post_ids.append(post.id)
    users_in_date_feed = {item.user:item.date for item in DateSortedItems.query.filter(DateSortedItems.user.in_(user_ids)).all()}
    posts_in_date_feed = {item.post:item.date for item in DateSortedItems.query.filter(DateSortedItems.post.in_(post_ids)).all()}
    print users_in_date_feed
    print posts_in_date_feed
    for result in results:
        if result['type'] == 'user':
            result['timestamp'] = maketimestamp(users_in_date_feed.get(result['user']['id']))
        elif result['type'] == 'post':
            result['timestamp'] = maketimestamp(posts_in_date_feed.get(result['post']['id']))
    return {'results' : results}
    print posts
    
def delete_from_central_queue(item_type, item_id):
    type_dict = {
            'user' : CentralQueueMobile.user,
            'post' : CentralQueueMobile.post,
            'question' : CentralQueueMobile.question
        }
    CentralQueueMobile.query.filter(type_dict[item_type] == item_id).delete()
    db.session.commit()
    return {'success' : True} 

def get_celebs_asked_today(offset, limit):
    from datetime import datetime, timedelta
    today = datetime.now() + timedelta(minutes = 330) 
    start_time = datetime(today.year, today.month, today.day, 0 ,0 ,0)
    result = db.session.execute(text('SELECT question_to, users.id, users.username, users.first_name, users.profile_picture, users.user_type, users.user_title, count(*) from questions join users on users.id = questions.question_to where timestamp > :today group by question_to order by count(*) desc'),params={'today' :start_time })
    resp = []
    for row in result:
        user = thumb_user_to_dict(row)
        user['questions_count'] = row['count(*)']
        resp.append(user)
    return {'results':resp}

def get_questions_asked_today(user_id, offset, limit):
    from datetime import datetime, timedelta
    today = datetime.now() + timedelta(minutes = 330) 
    start_time = datetime(today.year, today.month, today.day, 0 ,0 ,0)
    result = db.session.execute(text('SELECT * from questions where question_to = :user_id and timestamp > :today order by timestamp desc'), params={'today':start_time, 'user_id':user_id})
    resp = []
    for row in result:
        resp.append(question_to_dict(row))
    return {'results':resp}

def get_monks():
    return User.query.filter(User.monkness == 0).all()

def increase_followers(user_id, count):
    for u in get_monks()[:count]:
        f = Follow(user= u.id, followed=user_id)
        db.session.add(f)
    db.session.commit()

def increase_upvotes(question_id, count):
    for u in get_monks()[:count]:
        upvote = Upvote(question_id, u.id)
        db.session.add(upvote)
    db.session.commit()

def upvote_questions_of(username, count):
    from random import randint
    user = User.query.filter(User.username == username).first()
    if not user:
        return 'User not found'
    questions = Question.query.filter(Question.question_to == user.id, Question.is_answered == False).all()
    for question in questions:
        increase_upvotes(question.id, randint(count - 5, count))

def update_total_view_count(user_id, count):
    User.query.filter(User.id == user_id).update({'total_view_count':count})
    db.session.commit()

def admin_search_default(cur_user_id = None):
    from collections import defaultdict
    categories_order = ['Trending Now', 'Politicians', 'Authors', 'New on Frankly', 'Singers', 'Actors', 'Radio Jockeys', 'Chefs', 'Entrepreneurs', 'Subject Experts']
    
    results = db.session.execute(text("""SELECT search_defaults.category, users.id, users.username, users.first_name,
                                                    users.user_type, users.user_title, users.profile_picture,
                                                    users.bio, users.gender,
                                                    (SELECT count(*) FROM user_follows
                                                        WHERE user_follows.user=:cur_user_id
                                                            AND user_follows.followed=users.id
                                                            AND user_follows.unfollowed=false) AS is_following
                                            FROM users JOIN search_defaults ON users.id=search_defaults.user
                                            WHERE search_defaults.category IN :categories
                                            ORDER BY search_defaults.score"""),
                                        params = {'cur_user_id':cur_user_id, 'categories':categories_order}
                                )
    category_results = defaultdict(list)
    for row in results:
        user_dict = {'id':row[1],
                    'username':row[2],
                    'first_name':row[3],
                    'last_name':None,
                    'user_type':row[4],
                    'user_title':row[5],
                    'profile_picture':row[6],
                    'bio':row[7],
                    'gender':row[8],
                    'is_following':bool(row[9])
                    }
        category_results[row[0]].append(user_dict)


    for category, users in category_results.items():
        category_results[category] = category_results[category]

    resp = []
    for cat in categories_order:
        if category_results.get(cat):
            resp.append({'category_name':cat, 'users':category_results[cat]})

    return {'results':resp}

def add_to_date_sorted(_type, obj_id, timestamp, score = 0):
    '''
    timestamp must be in seconds never in seconds
    '''
    type_dict = {
                'user' : DateSortedItems.user,
                'post' : DateSortedItems.post
            }
    item = DateSortedItems.query.filter(type_dict[_type] == obj_id).first()
    if not item:
        item = DateSortedItems(_type, obj_id)
    item.date = datetime.datetime.fromtimestamp(timestamp)
    db.session.add(item)
    db.session.commit()
    return {'success' : True}

def _get_users_for_date_sorted_list(items):
    if not items:
        return items
    users_dict = {item.user:{'score':item.score,'date':item.date} for item in items}
    user_objs = db.session.execute(text('SELECT * FROM users WHERE id in :user_ids'), params = {'user_ids':users_dict.keys()})
    res_list = []
    for user in user_objs:
        user_dict = {}
        user_dict['type'] = 'user'
        user_dict['score'] = users_dict[user.id]['score']
        user_dict['timestamp'] = maketimestamp(users_dict[user.id]['date'])
        user_thumb = thumb_user_to_dict(user)
        user_dict['user'] = user_thumb
        res_list.append(user_dict)
    return res_list

def _get_posts_for_date_sorted_list(items):
    if not items:
        return items
    posts_dict = {item.post:{'score':item.score,'date':item.date} for item in items}
    post_objs = db.session.execute(text('SELECT * FROM posts WHERE id in :post_ids'), params = {'post_ids':posts_dict.keys()})
    post_objs = list(post_objs)
    post_thumbs = posts_to_dict(post_objs)
    res_list = []
    for post in post_thumbs:
        post_dict = {'type':'post'}
        post_dict['score'] = posts_dict[post['id']]['score']
        post_dict['timestamp'] = maketimestamp(posts_dict[post['id']]['date'])
        post_dict['post'] = post
        res_list.append(post_dict)
    return res_list
    
def get_date_sorted_list(offset=0, limit=100):
    items = DateSortedItems.query.all()
    users = filter(lambda x:x if x.user else False, items)  # users in DateSortedItems
    posts = filter(lambda x:x if x.post else False, items) # posts in DateSortedItems
    user_thumbs = _get_users_for_date_sorted_list(users)
    post_thumbs = _get_posts_for_date_sorted_list(posts)
    res = []
    res.extend(user_thumbs)
    res.extend(post_thumbs)
    res = sorted(res, key=lambda x:x['score'])
    return {'result' : res}

def update_date_feed_order(date, items):
    '''
    item contains obj_id, score, type
    '''
    type_dict = {
                'user' : DateSortedItems.user,
                'post' : DateSortedItems.post
            }
    date = datetime.datetime.fromtimestamp(date)
    for item in items:
        print item
        d = DateSortedItems.query.filter(type_dict[item['type']] == item['obj_id'], DateSortedItems.date == date).first()
        if d:
            d.score = item['score']
        db.session.add(d)
    db.session.commit()
    return {'success':True}

def delete_date_sorted_item(_type, obj_id):
    type_dict = {
                'user' : DateSortedItems.user,
                'post' : DateSortedItems.post
            }
    DateSortedItems.query.filter(type_dict[_type] == obj_id).delete()
    db.session.commit()
    return {'success' : True}