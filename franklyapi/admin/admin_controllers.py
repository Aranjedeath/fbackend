from models import *
from object_dict import *
from app import db

def user_list(user_type, deleted=False, offset=0, limit=10, order_by='user_since', order_desc=True):
    user_query = User.query.filter(User.user_type==user_type, User.deleted==deleted)

    if order_by == 'user_since':
        if order_desc:
            user_query.order_by(User.user_since.desc())


def question_list(offset, limit, user_to=[], user_from=[], public=True, deleted=False):
    questions = Question.query.filter(Question.deleted==deleted, Question.public==public,
                                    ).order_by(Question.timestamp.desc()
                                    ).offset(offset
                                    ).limit(limit
                                    ).all()
    return {'questions': [question_to_dict(question) for question in questions], 'next_index':offset+limit}

def delete_question(question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':True})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def undelete_question(question_id):
    Question.query.filter(Question.id==question_id).update({'deleted':False})
    db.session.commit()
    return {'success':True, 'question_id':question_id}

def edit_question(question_id, body):
    Question.query.filter(Question.id==question_id).update({'body':body.capitlize()})
    db.session.commit()
    return {'success':True, 'question_id':question_id}
