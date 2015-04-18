import time
import os


def location_dict(lat, lon, location_name, country_name, country_code):
    if not lat or lon:
        coordinate_point = None
    else:
        coordinate_point = [lat, lon]
    return {
            'coordinate_point':{'coordinates':coordinate_point},
            'location_name':location_name,
            'country_name':country_name,
            'country_code':country_code
            }

def media_dict(media_url, thumbnail_url):
    return {
            'media_url': media_url,
            'thumbnail_url': thumbnail_url,
            }

def user_to_dict(user):
    from configs import config
    from controllers import get_video_states
    from util import get_users_stats
    
    user_stats = get_users_stats([user.id])

    user_dict = {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'facebook_id': user.facebook_id,
        'twitter_id': user.twitter_id,
        'instagram_id': user.twitter_id,
        'google_id': user.google_id,
        'first_name': user.first_name,
        'last_name': None,
        'bio': user.bio or config.DEFAULT_BIO,
        'profile_picture': user.profile_picture,
        'cover_picture': user.cover_picture,
        'profile_video': user.profile_video,
        'gender': user.gender,
        'follower_count': user_stats[user.id]['follower_count'],
        'following_count': user_stats[user.id]['following_count'],
        'answer_count': user_stats[user.id]['answer_count'],
        'likes_count': 0,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'last_updated': int(time.mktime(user.last_updated.timetuple())),
        'facebook_write_permission' : user.facebook_write_permission,
        'twitter_write_permission': user.twitter_write_permission,
        'admin_level':1 if user.id in config.ADMIN_USERS else 0,
        'view_count' : user_stats[user.id]['view_count'],
        'web_link':'http://frankly.me/{username}'.format(username=user.username),
        'channel_id':'user_{user_id}'.format(user_id=user.id),
        'profile_video_requested':user_stats[user.id]['is_requested'],
        
        'user_type':user.user_type,
        'user_title':user.user_title,
        'question_count': user_stats[user.id]['question_count'],
        'interests':[],
        'profile_videos':get_video_states({user.profile_video:user.cover_picture})[user.profile_video] if user.profile_video else {}
    }

    if user_dict['profile_video']:
        user_dict['answer_count'] = user_dict['answer_count']+1
    return user_dict


def guest_user_to_dict(user, current_user_id, cur_user_interest_tags=None):
    from configs import config
    from controllers import get_video_states
    from util import get_users_stats
    
    if user.deleted == True:
        return thumb_user_to_dict(user)
    
    user_stats = get_users_stats([user.id], cur_user_id=current_user_id)

    user_dict = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': None,
        'bio': user.bio or config.DEFAULT_BIO,
        'profile_picture': user.profile_picture,
        'cover_picture': user.cover_picture,
        'profile_video': user.profile_video,
        'gender': user.gender,
        'follower_count': user_stats[user.id]['follower_count'],
        'following_count': user_stats[user.id]['following_count'],
        'answer_count': user_stats[user.id]['answer_count'],
        'likes_count': 0,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'is_follower':False,
        'is_following':user_stats[user.id]['is_following'],
        'allow_anonymous_question': user.allow_anonymous_question,
        'view_count' : user_stats[user.id]['view_count'],
        'user_type':user.user_type,
        'user_title':user.user_title,
        'profile_videos':get_video_states({user.profile_video:user.cover_picture})[user.profile_video] if user.profile_video else {},
        'web_link':'http://frankly.me/{username}'.format(username=user.username),
        'channel_id':'user_{user_id}'.format(user_id=user.id),
        'profile_video_requested':user_stats[user.id]['is_requested'],
        'twitter_handle':user.twitter_handle
    }
    if user_dict['profile_video']:
        user_dict['answer_count'] = user_dict['answer_count']+1

    return user_dict

def guest_users_to_dict(users, current_user_id, cur_user_interest_tags=None):
    if not users:
        return []
    from configs import config
    from controllers import get_video_states
    from util import get_users_stats

    user_stats = get_users_stats([user.id for user in users], cur_user_id=current_user_id)
    
    user_dicts = []

    for user in users:

        user_dict = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': None,
            'bio': user.bio or config.DEFAULT_BIO,
            'profile_picture': user.profile_picture,
            'cover_picture': user.cover_picture,
            'profile_video': user.profile_video,
            'gender': user.gender,
            'follower_count': user_stats[user.id]['follower_count'],
            'following_count': user_stats[user.id]['following_count'],
            'answer_count': user_stats[user.id]['answer_count'],
            'likes_count': 0,
            'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
            'is_follower':False,
            'is_following':user_stats[user.id]['is_following'],
            'allow_anonymous_question': user.allow_anonymous_question,
            'view_count' : user_stats[user.id]['view_count'],
            'user_type':user.user_type,
            'user_title':user.user_title,
            'profile_videos':get_video_states({user.profile_video:user.cover_picture})[user.profile_video] if user.profile_video else {},
            'web_link':'http://frankly.me/{username}'.format(username=user.username),
            'channel_id':'user_{user_id}'.format(user_id=user.id),
            'profile_video_requested':user_stats[user.id]['is_requested']
        }
        if user_dict['profile_video']:
            user_dict['answer_count'] = user_dict['answer_count']+1
        user_dicts.append(user_dict)
    return user_dicts


def invitable_to_dict(invitable, current_user_id):
    from controllers import has_invited, get_invite_count
    invitable_dict = {
            'id' : invitable.id,
            'first_name' : invitable.name,
            'last_name' : None,
            'username' : invitable.twitter_handle,
            'twitter_handle' : invitable.twitter_handle,
            'email' : invitable.email,
            'twitter_text' : invitable.twitter_text,
            'mail_text' : invitable.mail_text,
            'has_invited' : has_invited(current_user_id, invitable.id) if current_user_id else False,
            'cur_invite_count' : get_invite_count(invitable.id)+1,
            'max_invite_count' : invitable.max_invite_count,
            'profile_picture' : invitable.profile_picture,
            'user_title' : invitable.user_title,
            'bio' : invitable.bio

        }
    return invitable_dict

def thumb_user_to_dict(user, current_user_id=None):
    from configs import config
    from controllers import is_following
    user_dict = {
        'id':user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': None,
        'profile_picture': user.profile_picture,
        'gender':user.gender,
        'user_type':user.user_type,
        'bio' : user.bio or config.DEFAULT_BIO,
        'allow_anonymous_question' : user.allow_anonymous_question,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'user_title':user.user_title,
        'is_following':is_following(user.id, current_user_id) if current_user_id else False,
        'channel_id':'user_{user_id}'.format(user_id=user.id)
    }
    return user_dict

def make_celeb_questions_dict(celeb, questions, current_user_id=None):
    from controllers import get_question_upvote_count, is_following,\
        is_upvoted, get_upvoters, get_thumb_users, is_question_remindable

    upvoters = []
    for question in questions:
        upvoters.extend(get_upvoters(question.id, count=5))
    
    users = get_thumb_users(set([question.question_author for question in questions]+upvoters))

    celeb_dict =   {   
                    'id': celeb.id,
                    'username': celeb.username,
                    'first_name': celeb.first_name,
                    'last_name': None,
                    'profile_picture': celeb.profile_picture,
                    'gender': celeb.gender,
                    'user_title': celeb.user_title,
                    'user_type':celeb.user_type,
                    'is_following': is_following(celeb.id, current_user_id),
                    'bio':celeb.bio,
                    'channel_id':'user_{user_id}'.format(user_id=celeb.id),
                    'questions':[],
                    'twitter_handle': celeb.twitter_handle
                }
    for question in questions:
        ques_dict = {
        'id': question.id,
        'question_author': {
                            'id':users[question.question_author]['id'],
                            'username': users[question.question_author]['username'] if not question.is_anonymous else 'Anonymous',
                            'first_name': users[question.question_author]['first_name'] if not question.is_anonymous else 'Anonymous',
                            'last_name': None,
                            'profile_picture': users[question.question_author]['profile_picture'] if not question.is_anonymous else None,
                            'gender':users[question.question_author]['gender'],
                            'channel_id':'                                      user_{user_id}'.format(user_id=question.question_author)
                            },
        'question_to':{
                        'id':celeb.id,
                        'username': celeb.username,
                        'first_name': celeb.first_name,
                        'last_name': None,
                        'profile_picture': celeb.profile_picture,
                        'gender': celeb.gender,
                        'user_type': celeb.user_type,
                        'user_title': celeb.user_title,
                        'is_following':celeb_dict['is_following'],
                        'channel_id':'user_{user_id}'.format(user_id=celeb.id),
                        'twitter_handle':users[question.question_to]['twitter_handle'] if not question.open_question else None

                        },
        'tags': [],
        'body': question.body,        
        'timestamp': int(time.mktime(question.timestamp.timetuple())),
        'location': location_dict(question.lat, question.lon, question.location_name, question.country_name, question.country_code),
        'is_anonymous' : question.is_anonymous,
        'ask_count': get_question_upvote_count(question.id),
        'askers': [{'id':users[upvoter]['id'], 'profile_picture':users[upvoter]['profile_picture'], 'gender':users[upvoter]['gender']} for upvoter in upvoters],
        'background_image':"http://api.frankly.me/question/bg_image/%s"%(str(question.id)),
        'is_voted': is_upvoted(question.id, current_user_id) if current_user_id else False,
        'web_link':'http://frankly.me',
        'slug':question.slug,
        'is_remindable':is_question_remindable(question.id,current_user_id) if current_user_id else False
        }
        celeb_dict['questions'].append(ques_dict)
    return celeb_dict



def questions_to_dict(questions, cur_user_id=None):
    if not questions:
        return []
    from controllers import get_question_upvote_count, is_upvoted, get_thumb_users,\
        get_post_id_from_question_id, is_question_remindable


    user_ids = []
    for question in questions:
        user_ids.append(question.question_to)
        user_ids.append(question.question_author)

    users = get_thumb_users(user_ids, cur_user_id=cur_user_id)

    questions_dict = []

    for question in questions:
        ques_dict = {
            'id': question.id,
            'question_author': {
                                'id':users[question.question_author]['id'],
                                'username': users[question.question_author]['username'] if not question.is_anonymous else 'Anonymous',
                                'first_name': users[question.question_author]['first_name'] if not question.is_anonymous else 'Anonymous',
                                'last_name': None,
                                'profile_picture': users[question.question_author]['profile_picture'] if not question.is_anonymous else None,
                                'gender':users[question.question_author]['gender'],
                                'channel_id':'user_{user_id}'.format(user_id=users[question.question_author]['id'])
                                },
            'question_to':{
                            'id':users[question.question_to]['id'] if not question.open_question else '00000',
                            'username': users[question.question_to]['username'] if not question.open_question else '00000',
                            'first_name': users[question.question_to]['first_name'] if not question.open_question else '00000',
                            'last_name': None,
                            'profile_picture': users[question.question_to]['profile_picture'] if not question.open_question else None,
                            'gender': users[question.question_to]['gender'] if not question.open_question else None,
                            'user_type': users[question.question_to]['user_type'] if not question.open_question else 0,
                            'user_title': users[question.question_to]['user_title'] if not question.open_question else '00000',
                            'is_following':users[question.question_to]['is_following'] if not question.open_question else '0000',
                            'channel_id':'user_{user_id}'.format(user_id=users[question.question_to]['id']) if not question.open_question else '0000',
                            'twitter_handle':users[question.question_to]['twitter_handle'] if not question.open_question else None

                            },
            'tags': [],
            'body': question.body,        
            'timestamp': int(time.mktime(question.timestamp.timetuple())),
            'location': location_dict(question.lat, question.lon, question.location_name, question.country_name, question.country_code),
            'is_anonymous' : question.is_anonymous,
            'ask_count': get_question_upvote_count(question.id)+1,
            #'askers': [{'id':users[upvoter]['id'], 'profile_picture':users[upvoter]['profile_picture'], 'gender':users[upvoter]['gender']} for upvoter in upvoters],
            'background_image':"http://dev.frankly.me/question/bg_image/%s"%(str(question.id)),
            'is_voted': is_upvoted(question.id, cur_user_id) if cur_user_id else False,
            'web_link':'http://frankly.me/q/{short_id}'.format(short_id=question.short_id),
            'short_id': question.short_id,
            'is_answered':question.is_answered,
            'score':question.score,
            'slug':question.slug,
            'open_question':question.open_question,
            'is_remindable':is_question_remindable(question.id,cur_user_id) if cur_user_id else False
        }
        if question.is_answered:
            ques_dict['post_id'] = get_post_id_from_question_id(question.id)
        questions_dict.append(ques_dict)

    return questions_dict


def question_to_dict(question, cur_user_id=None):
    from controllers import get_question_upvote_count, is_upvoted, get_thumb_users, get_post_id_from_question_id, is_question_remindable
    
    #upvoters = get_upvoters(question.id, count=5)
    users = get_thumb_users([question.question_author, question.question_to], cur_user_id=cur_user_id)

    ques_dict = {
        'id': question.id,
        'question_author': {
                            'id':users[question.question_author]['id'],
                            'username': users[question.question_author]['username'] if not question.is_anonymous else 'Anonymous',
                            'first_name': users[question.question_author]['first_name'] if not question.is_anonymous else 'Anonymous',
                            'last_name': None,
                            'profile_picture': users[question.question_author]['profile_picture'] if not question.is_anonymous else None,
                            'gender':users[question.question_author]['gender'],
                            'channel_id':'user_{user_id}'.format(user_id=users[question.question_author]['id'])
                            
                            },

         'question_to':{
                            'id':users[question.question_to]['id'] if not question.open_question else '00000',
                            'username': users[question.question_to]['username'] if not question.open_question else '00000',
                            'first_name': users[question.question_to]['first_name'] if not question.open_question else '00000',
                            'last_name': None,
                            'profile_picture': users[question.question_to]['profile_picture'] if not question.open_question else None,
                            'gender': users[question.question_to]['gender'] if not question.open_question else None,
                            'user_type': users[question.question_to]['user_type'] if not question.open_question else 0,
                            'user_title': users[question.question_to]['user_title'] if not question.open_question else '00000',
                            'is_following':users[question.question_to]['is_following'] if not question.open_question else '0000',
                            'channel_id':'user_{user_id}'.format(user_id=users[question.question_to]['id']) if not question.open_question else '0000',
                            'twitter_handle':users[question.question_to]['twitter_handle'] if not question.open_question else None
                            },
        'tags': [],
        'body': question.body,        
        'timestamp': int(time.mktime(question.timestamp.timetuple())),
        'location': location_dict(question.lat, question.lon, question.location_name, question.country_name, question.country_code),
        'is_anonymous' : question.is_anonymous,
        'ask_count': get_question_upvote_count(question.id)+1,
        #'askers': [{'id':users[upvoter]['id'], 'profile_picture':users[upvoter]['profile_picture'], 'gender':users[upvoter]['gender']} for upvoter in upvoters],
        'background_image':"http://dev.frankly.me/question/bg_image/%s"%(str(question.id)),
        'is_voted': True if question.question_author==cur_user_id else is_upvoted(question.id, cur_user_id) if cur_user_id else False,
        'web_link':'http://frankly.me/q/{short_id}'.format(short_id=question.short_id),
        'short_id': question.short_id,
        'is_answered':question.is_answered,
        'score':question.score,
        'slug':question.slug,
        'open_question':question.open_question,
        'is_remindable':is_question_remindable(question.id,cur_user_id) if cur_user_id else False

    }
    if question.is_answered:
        ques_dict['post_id'] = get_post_id_from_question_id(question.id)
    return ques_dict

def post_to_dict(post, cur_user_id=None, distance=None, include_comments=3):
    from configs import config
    from controllers import get_video_states, get_questions, get_thumb_users, get_posts_stats, get_comments_for_posts
    from util import get_users_stats
    users = get_thumb_users([post.question_author, post.answer_author], cur_user_id=cur_user_id)
    questions = get_questions([post.question], cur_user_id=cur_user_id)
    
    post_stats = get_posts_stats([post.id], cur_user_id=cur_user_id)
    user_stats = get_users_stats([post.answer_author], cur_user_id=cur_user_id)
    if include_comments:
        all_comments = get_comments_for_posts(cur_user_id, [post.id], offset=0, limit=include_comments)

    
    post_dict = {
        'id': post.id,
        'question_author': {
            'id':users[post.question_author]['id'] if not questions[post.question]['is_anonymous'] else '',
            'username': users[post.question_author]['username'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
            'first_name': users[post.question_author]['first_name'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
            'last_name': None,
            'gender': users[post.question_author]['gender'],
            'profile_picture': users[post.question_author]['profile_picture'] if not questions[post.question]['is_anonymous'] else None,
            'channel_id':'user_{user_id}'.format(user_id=users[post.question_author]['id'])
        },
        'answer_author': {
            'id':users[post.answer_author]['id'],
            'username':users[post.answer_author]['username'],
            'first_name': users[post.answer_author]['first_name'],
            'last_name': None,
            'profile_picture': users[post.answer_author]['profile_picture'],
            'location': users[post.answer_author]['location'],
            'gender': users[post.answer_author]['gender'],
            'bio':users[post.answer_author]['bio'] or config.DEFAULT_BIO,
            'user_type':users[post.answer_author]['user_type'],
            'user_title':users[post.answer_author]['user_title'],
            'allow_anonymous_question': users[post.answer_author]['user_title'],
            'is_following':users[post.answer_author]['is_following'],
            'follower_count': user_stats[post.answer_author]['follower_count'],
            'channel_id':'user_{user_id}'.format(user_id=users[post.answer_author]['id'])

        },
        'question': {
                'id':questions[post.question]['id'],
                'body': questions[post.question]['body'],
                'question_type': 'text',
                'timestamp': int(time.mktime(questions[post.question]['timestamp'].timetuple())),
                'tags': [],
                'is_anonymous': bool(questions[post.question]['is_anonymous']),
                'slug':questions[post.question]['slug'],
                'open_question':questions[post.question]['open_question']
        },
        'answer': {
            'body': '',
            'media': media_dict(post.media_url, post.thumbnail_url),
            'type': post.answer_type,
            'timestamp': int(time.mktime(post.timestamp.timetuple())),
            'tags': [],
            'media_urls':get_video_states({post.media_url:post.thumbnail_url})[post.media_url]
        },

        'liked_count': post_stats[post.id]['like_count'],
        # to store count and list of user ids
        'comment_count': post_stats[post.id]['comment_count'],
        'is_liked': post_stats[post.id]['is_liked'],
        'deleted': post.deleted,
        'tags':[],
        'location': location_dict(post.lat, post.lon, post.location_name, post.country_name, post.country_code),
        'distance':distance,
        'client_id':post.client_id,
        'ready':post.ready,
        'popular':post.popular,
        'view_count':post_stats[post.id]['view_count'],
        'web_link':'http://frankly.me/p/{client_id}'.format(client_id=post.client_id),
        'whatsapp_share_count':post_stats[post.id]['whatsapp_share_count'],
        'other_share_count':post_stats[post.id]['other_share_count'],
        'comments':all_comments[post.id] if include_comments else {}
    }
    post_dict['answer']['media']['thumbnail_url'] = post_dict['answer']['media_urls']['thumb']
    return post_dict



def posts_to_dict(posts, cur_user_id=None, distance=None, include_comments=3):
    if not posts:
        return []

    from configs import config
    from controllers import get_video_states, get_questions, get_thumb_users, get_posts_stats, get_comments_for_posts
    from util import get_users_stats
    
    user_list = set()
    answer_media_urls = {}
    question_ids = []
    post_ids = []
    
    for p in posts:
        user_list.add(p.question_author)
        user_list.add(p.answer_author)
        answer_media_urls[p.media_url] = p.thumbnail_url
        question_ids.append(p.question)
        post_ids.append(p.id)

    users = get_thumb_users(user_list, cur_user_id=cur_user_id)
    media_urls = get_video_states(answer_media_urls)
    questions = get_questions(question_ids, cur_user_id=cur_user_id)
    post_stats = get_posts_stats(post_ids, cur_user_id)
    user_stats = get_users_stats(user_list, cur_user_id)
    
    if include_comments:
        all_comments = get_comments_for_posts(cur_user_id, post_ids, offset=0, limit=include_comments)

    posts_dict = []
    for post in posts:
        
        p_dict = {
            'id': post.id,
            'question_author': {
                'id':users[post.question_author]['id'] if not questions[post.question]['is_anonymous'] else '',
                'username': users[post.question_author]['username'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
                'first_name': users[post.question_author]['first_name'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
                'last_name': None,
                'gender': users[post.question_author]['gender'],
                'profile_picture': users[post.question_author]['profile_picture'] if not questions[post.question]['is_anonymous'] else None,
                'channel_id':'user_{user_id}'.format(user_id=users[post.question_author]['id'])
            },
            'answer_author': {
                'id':users[post.answer_author]['id'],
                'username':users[post.answer_author]['username'],
                'first_name': users[post.answer_author]['first_name'],
                'last_name': None,
                'profile_picture': users[post.answer_author]['profile_picture'],
                'location': users[post.answer_author]['location'],
                'gender': users[post.answer_author]['gender'],
                'bio':users[post.answer_author]['bio'] or config.DEFAULT_BIO,
                'user_type':users[post.answer_author]['user_type'],
                'user_title':users[post.answer_author]['user_title'],
                'allow_anonymous_question': users[post.answer_author]['user_title'],
                'is_following':users[post.answer_author]['is_following'],
                'follower_count': user_stats[post.answer_author]['follower_count'],
                'channel_id':'user_{user_id}'.format(user_id=users[post.answer_author]['id'])

            },
            'question': {
                'id':questions[post.question]['id'],
                'body': questions[post.question]['body'],
                'question_type': 'text',
                'timestamp': int(time.mktime(questions[post.question]['timestamp'].timetuple())),
                'tags': [],
                'is_anonymous': bool(questions[post.question]['is_anonymous']),
                'slug':questions[post.question]['slug'],
                'open_question':questions[post.question]['open_question']
            },
            'answer': {
                'body': '',
                'media': media_dict(post.media_url, post.thumbnail_url),
                'type': post.answer_type,
                'timestamp': int(time.mktime(post.timestamp.timetuple())),
                'tags': [],
                'media_urls':media_urls[post.media_url]
            },
            'liked_count': post_stats[post.id]['like_count'],
            # to store count and list of user ids
            'comment_count': post_stats[post.id]['comment_count'],
            'is_liked': post_stats[post.id]['is_liked'],
            #'is_reshared': is_reshared(post.id, cur_user_id),
            'deleted': post.deleted,
            'tags':[],
            'location': location_dict(post.lat, post.lon, post.location_name, post.country_name, post.country_code),
            'distance':distance,
            'client_id':post.client_id,
            'ready':post.ready,
            'popular':post.popular,
            'view_count':post_stats[post.id]['view_count'],
            'web_link':'http://frankly.me/p/{client_id}'.format(client_id=post.client_id),
            'whatsapp_share_count':post_stats[post.id]['whatsapp_share_count'],
            'other_share_count':post_stats[post.id]['other_share_count'],
            'comments':all_comments[post.id] if include_comments else {}
        }
        p_dict['answer']['media']['thumbnail_url'] = p_dict['answer']['media_urls']['thumb']
        posts_dict.append(p_dict)


    return posts_dict





def comment_to_dict(comment):
    from controllers import get_thumb_users
    users = get_thumb_users([comment.comment_author])    
    comment_dict =  {
                        'id': comment.id,
                        'body': comment.body,
                        'comment_author': {
                            'id':users[comment.comment_author]['id'],
                            'profile_picture': users[comment.comment_author]['profile_picture'],
                            'username': users[comment.comment_author]['username'],
                            'first_name':users[comment.comment_author]['first_name'],
                            'last_name': None,
                            'gender':users[comment.comment_author]['gender'],
                            'channel_id':'user_{user_id}'.format(user_id=users[comment.comment_author]['id'])
                        },
                        'timestamp': int(time.mktime(comment.timestamp.timetuple())),
                        'on_post':comment.on_post
                    }
    return comment_dict

def comments_to_dict(comments):
    from controllers import get_thumb_users
    users = get_thumb_users([comment.comment_author for comment in comments])
    
    comments_dict = []
    for comment in comments:
        com_dict =  {
                        'id': comment.id,
                        'body': comment.body,
                        'comment_author': {
                            'id':users[comment.comment_author]['id'],
                            'profile_picture': users[comment.comment_author]['profile_picture'],
                            'username': users[comment.comment_author]['username'],
                            'first_name':users[comment.comment_author]['first_name'],
                            'last_name': None,
                            'gender':users[comment.comment_author]['gender'],
                            'channel_id':'user_{user_id}'.format(user_id=users[comment.comment_author]['id'])
                        },
                        'timestamp': int(time.mktime(comment.timestamp.timetuple())),
                        'on_post':comment.on_post
                    }
        comments_dict.append(com_dict)

    return comments_dict


