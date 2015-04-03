from configs import config
key = {
    'question-ask-self_user' : {
        'title': '',
        'text': "<b><question_author_name></b> asked you '<question_body>'",
        'url': config.WEB_URL + '/q/%s',
        'label_one': 'Answer',
        'label_two': 'Later',
        'day_limit': 2

    },
    'post-add-self_user': {
        'title': '<b><answer_author_name></b> answered your question.',
        'text': "<b><answer_author_name></b> answered your question <question_body>",
        'url': config.WEB_URL + '/p/%s',
        'day_limit': 3,
        'positive_label': 'Play',
        'label_one': 'Play',
        'label_two': ''
    },
    'post-add-following_user': {
        'title': '<b><answer_author_name></b> answered a new question',
        'text': '''<question_author> answered the question <question_body>''',
        'url': config.WEB_URL + '/p/%s',
        'day_limit': 1,
        'label_one': 'Play',
        'label_two':''
    },
    'new-celebrity-followed_category': {
        'title':'',
        'text': '''<celebrity_name> has just joined Frankly. Ask him anything.''',
        'url': config.WEB_URL + '/%s',
        'day-limit': 1,
        'label_one': 'Ask Now',
        'label_two': 'Later'
    },
    'popular-question-self_user': {
        'title':'',
        'text': '''Your question "<question_body>" has received <upvote_count>+ upvotes. Share it to get more upvotes.''',
        'url': config.WEB_URL + '/q/%s',
        'day-limit': 1,
        'label_one':'',
        'label_two': ''
    },
    'user-followers-milestone': {
        'title':'',
        'text': 'You just got your <milestone_count>th follower. Get more by sharing your profile.',
        'url': config.WEB_URL + '/%s',
        'day-limit': 1,
        'label_one':'',
        'label_two': ''
    },
    'post-likes-milestone': {
        'title':'',
        'text': 'Your answer has crossed over <milestone_count> likes. Share it to become popular.',
        'url': config.WEB_URL + '/p/%s',
        'day-limit': 1,
        'label_one':'',
        'label_two': ''

    },
    'intro-video-request':{
         'title': 'You are in demand!',
         'text': '<requester_name> just asked you for an intro video.',
         'url': config.WEB_URL + '/%s',
         'day-limit': 1,
         'label_one':'',
         'label_two': ''
    }
}


def question_asked_text(question,question_author,question_to):
    text = key['question-ask-self_user']['text']
    if question.is_anonymous:
        text = text.replace('<question_author_name>', 'Anonymous')
    else:
        text = text.replace('<question_author_name>', question_author)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<question_to_name>', question_to)

    return text

def post_add(answer_author, question_body):
    text = key['post-add-self_user']['text']
    text = text.replace('<answer_author_name>', answer_author)
    text = text.replace('<question_body>', question_body)
    return text

def popular_question_text(question_body, upvote_count):
    text = key['popular-question-self_user']['text']
    return text.replace('<question_body>', question_body).replace('<upvote_count>', str(((upvote_count/10)*10)))

def following_answered_question(author_name, question_body):
    text = key['following-new-post']['text']
    return text.replace('<question_author>', author_name).replace('<question_body>', question_body)

def milestone_text(milestone_name, milestone_count):
    text = key[milestone_name]['text']
    return text.replace('<milestone_count>',milestone_count)

def user_profile_request(requester_name):
    text = key['intro-video-request']['text']
    return text.replace('<requester_name>', requester_name)

milestones = {
    'user-followers-milestone':[100, 200, 500, 1000, 5000, 10000, 20000, 50000, 1000000, 10000000],
    'post-likes-milestone': [100, 200, 500, 1000, 5000, 10000, 20000, 50000, 1000000, 10000000],
    'upvotes': [100, 200, 500, 1000, 5000, 10000, 20000, 50000, 1000000, 10000000],
    'profile_views': [100, 200, 500, 1000, 5000, 10000, 20000, 50000, 1000000, 10000000],
    'post_views':[100, 200, 500, 1000, 5000, 10000, 20000, 50000, 1000000, 10000000]

}

