from configs import config
key = {
    'question-ask-self_user' : {

        'text': "<b><question_author_name></b> asked you '<question_body>'",
        'url': config.WEB_URL + '/q/%s',
        'day-limit': 2

    },
    'post-add-self_user': {

        'text': "<b><answer_author_name></b> answered your question <question_body>",
        'url': config.WEB_URL + '/p/%s',
        'day-limit': 3
    },
    'new-celeb-user': {

    },
    'popular-question-self_user': {
        'text': '''Your question "<question_body>" has received <upvote_count>+ upvotes. Share it to get more upvotes.''',
        'url': config.WEB_URL + '/q/%s' ,
        'day-limit': 1
    }

    'following-new-post': {
        'text': '''<question_author> answered the question <question_body>''',
        'url': config.WEB_URL + '/p/%s',
        'day-limit': 1

    },
    'user_followers_milestone':{
        'text': 'You just got your <milestone_count>th follower. Get more by sharing your profile.',
        'url': config.WEB_URL + '%s',
        'day-limit': 1
    },
    'post_likes_milestone':{
        'text': 'Your answer has crossed over <milestone_count> likes. Share it to become popular.',
        'url': config.WEB_URL + '/p/%s',
        'day-limit': 1

    }

}


def question_asked_text(question,question_author,question_to):
    text = key['question-ask-self_user']['text']
    if question.is_anonymous:
        text = text.replace('<question_author_name>', 'Anonymous')
    else:
        text = text.replace('<question_author_name>', question_author.first_name)
    text = text.replace('<question_body>', question.body)
    text = text.replace('<question_to_name>', question_to.first_name)
    text = text.replace('<question_to_username>', question_to.username)
    text = text.replace('<question_author_username>', question_author.username)

    return text

def post_add(answer_author, question_body):
    text = key['post-add-self_user']['text']
    text = text.replace('<answer_author_name>', answer_author.first_name)
    text = text.replace('<question_body>', question_body)
    return text

def popular_question_text(question_body, upvote_count):
    text = key['popular-question-self_user']['text']
    return text.replace('<question_body>', question_body).replace('<upvote_count>', str(((upvote_count/10)*10)))

def following_answered_question(author_name, question_body):
    text = key['following-new-post']['text']
    return text.replace('<question_author', author_name).replace('<question_body>', question_body)

def milestone_text(milestone_name, milestone_count):
    text = key[milestone_name]['text']
    return text.replace('<milestone_count>',milestone_count)


milestones = {
    'user_followers':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'post_likes':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'upvotes':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'profile_views':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    },
    'post_views':{
        '100'       :100,
        '200'       :200,
        '500'       :500,
        '1000'      :1000,
        '5000'      :5000,
        '10000'     :10000,
        '20000'     :20000,
        '50000'     :50000,
        '1000000'   :1000000,
        '10000000'  :10000000,
    }

}

