from models import *

def user_list(user_type, deleted=False, offset=0, limit=10, order_by='user_since', order_desc=True):
	user_query = User.query.filter(User.user_type==user_type, User.deleted==deleted)

	if order_by == 'user_since':
		if order_desc:
			user_query.order_by(User.user_since.desc())


def question_list(offset, limit, user_to=[], user_from=[], public=True, deleted=False):
	question = Question.query.filter(Question.deleted==deleted, Question.public==public
									).offset(offset
									).limit(limit
									).all()
	

	