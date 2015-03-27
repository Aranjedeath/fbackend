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