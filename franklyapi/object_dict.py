import time


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
    from controllers import get_video_states, get_user_stats
    
    user_stats = get_user_stats(user.id)

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
        'follower_count': user_stats['follower_count'],
        'following_count': user_stats['following_count'],
        'answer_count': user_stats['answer_count'],
        'likes_count': 0,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'last_updated': int(time.mktime(user.last_updated.timetuple())),
        'fb_write_perm' : user.facebook_write_permission,
        'fb_perm':'none',
        'admin_level':1 if user.id in config.ADMIN_USERS else 0,
        'view_count' : user_stats['view_count'],
        'web_link':'http://frankly.me/{username}'.format(username=user.username),
        
        'user_type':user.user_type,
        'user_title':user.user_title,
        'interests':[],
        'profile_videos':get_video_states({user.profile_video:user.cover_picture})[user.profile_video] if user.profile_video else {}
    }

    if user_dict['profile_video']:
        user_dict['answer_count'] = user_dict['answer_count']+1
    return user_dict


def guest_user_to_dict(user, current_user_id, cur_user_interest_tags=None):
    from configs import config
    from controllers import get_video_states, get_user_stats, is_follower, is_following
    if user.deleted == True:
        return thumb_user_to_dict(user)
    
    user_stats = get_user_stats(user.id)

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
        'follower_count': user_stats['follower_count'],
        'following_count': user_stats['following_count'],
        'answer_count': user_stats['answer_count'],
        'likes_count': 0,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'is_follower':is_follower(user.id, current_user_id) if current_user_id else False,
        'is_following':is_following(user.id, current_user_id) if current_user_id else False,
        'allow_anonymous_question': user.allow_anonymous_question,
        'view_count' : user_stats['view_count'],
        'user_type':user.user_type,
        'user_title':user.user_title,
        'profile_videos':get_video_states({user.profile_video:user.cover_picture})[user.profile_video] if user.profile_video else {},
        'web_link':'http://frankly.me/{username}'.format(username=user.username)
    }
    if user_dict['profile_video']:
        user_dict['answer_count'] = user_dict['answer_count']+1
    
    return user_dict

def search_user_to_dict(user, current_user_id = None):
    user_dict = {
        'id':user.id,
        'username':user.username,
        'first_name':user.first_name,
        'last_name':None,
        'profile_picture':user.profile_picture,
        'user_type':user.user_type,
        'user_title':user.user_title
    }
    return user_dict

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
            'cur_invite_count' : get_invite_count(invitable.id),
            'max_invite_count' : invitable.max_invite_count,
            'profile_picture' : invitable.profile_picture,
            'user_title' : invitable.user_title,
            'bio' : invitable.bio

        }
    return invitable_dict

def thumb_user_to_dict(user):
    from configs import config
    user_dict = {
        'id':user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': None,
        'profile_picture': user.profile_picture,
        'deleted': user.deleted,
        'gender':user.gender,
        'bio' : user.bio or config.DEFAULT_BIO,
        'allow_anonymous_question' : user.allow_anonymous_question,
        'location': location_dict(user.lat, user.lon, user.location_name, user.country_name, user.country_code),
        'user_title':user.user_title
    }
    return user_dict

def make_celeb_questions_dict(celeb, questions, current_user_id=None):
    from controllers import get_question_upvote_count, is_following, is_upvoted, get_upvoters, get_thumb_users
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
                    'questions':[]
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
                            'gender':users[question.question_author]['gender']
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
                        'is_following':celeb_dict['is_following']

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
        'web_link':'http://frankly.me'
        }
        celeb_dict['questions'].append(ques_dict)
    return celeb_dict


def question_to_dict(question, current_user_id=None):
    from controllers import get_question_upvote_count, is_upvoted, get_upvoters,  get_thumb_users,is_following
    
    upvoters = get_upvoters(question.id, count=5)
    users = get_thumb_users([question.question_author, question.question_to]+upvoters)

    ques_dict = {
        'id': question.id,
        'question_author': {
                            'id':users[question.question_author]['id'],
                            'username': users[question.question_author]['username'] if not question.is_anonymous else 'Anonymous',
                            'first_name': users[question.question_author]['first_name'] if not question.is_anonymous else 'Anonymous',
                            'last_name': None,
                            'profile_picture': users[question.question_author]['profile_picture'] if not question.is_anonymous else None,
                            'gender':users[question.question_author]['gender']
                            },
        'question_to':{
                        'id':users[question.question_to]['id'],
                        'username': users[question.question_to]['username'],
                        'first_name': users[question.question_to]['first_name'],
                        'last_name': None,
                        'profile_picture': users[question.question_to]['profile_picture'],
                        'gender': users[question.question_to]['gender'],
                        'user_type': users[question.question_to]['user_type'],
                        'user_title': users[question.question_to]['user_title'],
                        'is_following':is_following(celeb.id, current_user_id)

                        },
        'tags': [],
        'body': question.body,        
        'timestamp': int(time.mktime(question.timestamp.timetuple())),
        'location': location_dict(question.lat, question.lon, question.location_name, question.country_name, question.country_code),
        'is_anonymous' : question.is_anonymous,
        'ask_count': get_question_upvote_count(question.id)+1,
        'askers': [{'id':users[upvoter]['id'], 'profile_picture':users[upvoter]['profile_picture'], 'gender':users[upvoter]['gender']} for upvoter in upvoters],
        'background_image':"http://dev.frankly.me/question/bg_image/%s"%(str(question.id)),
        'is_voted': is_upvoted(question.id, current_user_id) if current_user_id else False,
        'web_link':'http://frankly.me'
    }
    return ques_dict

def post_to_dict(post, cur_user_id=None, distance=None):
    from configs import config
    from controllers import get_video_states, is_liked, is_reshared, get_questions, is_following, get_thumb_users, get_post_stats, get_user_stats
    users = get_thumb_users([post.question_author, post.answer_author])
    questions = get_questions([post.question])
    
    post_stats = get_post_stats(post.id)
    answer_author_stats = get_user_stats(post.answer_author)
    
    post_dict = {
        'id': post.id,
        'question_author': {
            'id':users[post.question_author]['id'] if not questions[post.question]['is_anonymous'] else '',
            'username': users[post.question_author]['username'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
            'first_name': users[post.question_author]['first_name'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
            'last_name': None,
            'gender': users[post.question_author]['gender'],
            'profile_picture': users[post.question_author]['profile_picture'] if not questions[post.question]['is_anonymous'] else None,
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
            'is_following':is_following(post.answer_author, cur_user_id) if cur_user_id else False,
            'follower_count': answer_author_stats['follower_count']

        },
        'question': {
                'id':questions[post.question]['id'],
                'body': questions[post.question]['body'],
                'question_type': 'text',
                'timestamp': int(time.mktime(questions[post.question]['timestamp'].timetuple())),
                'tags': [],
                'is_anonymous': bool(questions[post.question]['is_anonymous'])
        },
        'answer': {
            'body': '',
            'media': media_dict(post.media_url, post.thumbnail_url),
            'type': post.answer_type,
            'timestamp': int(time.mktime(post.timestamp.timetuple())),
            'tags': [],
            'media_urls':get_video_states({post.media_url:post.thumbnail_url})[post.media_url]
        },

        'liked_count': post_stats['like_count'],
        'is_reshared': is_reshared(post.id, cur_user_id),
        # to store count and list of user ids
        'comment_count': post_stats['comment_count'],
        'is_liked': is_liked(post.id, cur_user_id),
        'deleted': post.deleted,
        'tags':[],
        'location': location_dict(post.lat, post.lon, post.location_name, post.country_name, post.country_code),
        'distance':distance,
        'client_id':post.client_id,
        'ready':post.ready,
        'popular':post.popular,
        'view_count':post_stats['view_count'],
        'web_link':'http://frankly.me/p/{client_id}'.format(client_id=post.client_id)
    }
    post_dict['answer']['media']['thumbnail_url'] = post_dict['answer']['media_urls']['thumb']
    return post_dict



def posts_to_dict(posts, cur_user_id=None, distance=None):
    from configs import config
    from controllers import get_video_states, get_questions, is_liked, is_reshared, is_following, get_thumb_users, get_post_stats, get_user_stats
    user_list = set()
    answer_media_urls = {}
    question_ids = []
    
    for p in posts:
        user_list.add(p.question_author)
        user_list.add(p.answer_author)
        answer_media_urls[p.media_url] = p.thumbnail_url
        question_ids.append(p.question)

    users = get_thumb_users(user_list)
    media_urls = get_video_states(answer_media_urls)
    questions = get_questions(question_ids)


    posts_dict = []
    for post in posts:
        
        post_stats = get_post_stats(post.id)
        answer_author_stats = get_user_stats(post.answer_author)
        
        p_dict = {
            'id': post.id,
            'question_author': {
                'id':users[post.question_author]['id'] if not questions[post.question]['is_anonymous'] else '',
                'username': users[post.question_author]['username'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
                'first_name': users[post.question_author]['first_name'] if not questions[post.question]['is_anonymous'] else 'Anonymous',
                'last_name': None,
                'gender': users[post.question_author]['gender'],
                'profile_picture': users[post.question_author]['profile_picture'] if not questions[post.question]['is_anonymous'] else None,
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
                'is_following':is_following(post.answer_author, cur_user_id) if cur_user_id else False,
                'follower_count': answer_author_stats['follower_count']

            },
            'question': {
                'id':questions[post.question]['id'],
                'body': questions[post.question]['body'],
                'question_type': 'text',
                'timestamp': int(time.mktime(questions[post.question]['timestamp'].timetuple())),
                'tags': [],
                'is_anonymous': bool(questions[post.question]['is_anonymous'])
            },
            'answer': {
                'body': '',
                'media': media_dict(post.media_url, post.thumbnail_url),
                'type': post.answer_type,
                'timestamp': int(time.mktime(post.timestamp.timetuple())),
                'tags': [],
                'media_urls':media_urls[post.media_url]
            },
            'liked_count': post_stats['like_count'],
            # to store count and list of user ids
            'comment_count': post_stats['comment_count'],
            'is_liked': is_liked(post.id, cur_user_id),
            'is_reshared': is_reshared(post.id, cur_user_id),
            'deleted': post.deleted,
            'tags':[],
            'location': location_dict(post.lat, post.lon, post.location_name, post.country_name, post.country_code),
            'distance':distance,
            'client_id':post.client_id,
            'ready':post.ready,
            'popular':post.popular,
            'view_count':post_stats['view_count'],
            'web_link':'http://frankly.me/p/{client_id}'.format(client_id=post.client_id)
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
                            'gender':users[comment.comment_author]['gender']
                        },
                        'timestamp': int(time.mktime(comment.timestamp.timetuple())),
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
                            'gender':users[comment.comment_author]['gender']
                        },
                        'timestamp': int(time.mktime(comment.timestamp.timetuple())),
                    }
        comments_dict.append(com_dict)

    return comments_dict


