CATEGORIES = { 'questionAskedToMe' : {'weight':1,'info':['question_author_is_celeb','qauthor_degree_from_me','qauthor_score','me']},
	'answerOnMyQuestion' : {'weight':15,'info':['me']},
	'commentOnMyQuestion' : {'weight':1,'info':['comment_author_is_celeb','cauthor_degree_from_me','cauthor_score','me']},
	'commentsOnMyQuestion' : {'weight':1,'info':['comments_now','comments_before']},
	'viewsOnMyQuestion' : {'weight':1,'info':['views_now','me']},
	'upvoteOnMyQuestion' : {'weight':1,'info':['upvote_author_is_celeb','uauthor_degree_from_me','uauthor_score','me']},
	'upvotesOnMyQuestion' : {'weight':1,'info':['upvotes_now','upvotes_before','me']},
	'commentOnMyAnswer' : {'weight':1,'info':['comment_author_is_celeb','cauthor_degree_from_me','cauthor_score','me']},
	'commentsOnMyAnswer' : {'weight':1,'info':['comments_now','comments_before','me']},
	'viewsOnMyAnswer' : {'weight':1,'info':['views_now','views_before','me']},
	'viewsOnMyProfile' : {'weight':1,'info':['views_now','views_before','me']},
	'followerOnMyProfile' : {'weight':1,'info':['follower_score','follower_degree','follower_celeb','me']},
	'followersOfMyProfile' : {'weight':1,'info':['followers_now','followers_before','me']},
	'likeOnMyAnswer' : {'weight':1,'info':['like_author_score','like_author_degree','like_author_celeb','likes_before','me']},
	'likesOnMyAnswer' : {'weight':1,'info':['likes_now','likes_before','me']},
	'likeOnMyQuestion' : {'weight':1,'info':['like_author_score','like_author_degree','like_author_celeb','me']},
	'likesOnMyQuestion' : {'weight':1,'info':['likes_now','likes_before','me']},
	'upvoteOnQuestionToMe' : {'weight':1,'info':['upvote_author_is_celeb','uauthor_degree_from_me','uauthor_score','me']},
	'upvotesOnQuestionToMe' : {'weight':1,'info':['upvotes_before','upvotes_before']},
}

# Normalized => (0,1) , 7 , 8

def validate(data,info,category_name,me=None):
	try:
		if not data:
			return False
		if not data[category_name]:
			return False
		for inf in info:
			if inf == 'me':
				if not me:
					return False
			elif not data['inf']:
					return False
		return True
	except Exception as e:
		return False

## Score lies between (0,((degree_exp ** max_degree) * MAX(AUTHOR_SCORE) + celeb_score))

# add code for self as celeb
def calc_questionAskedToMe(data,me=None):
	celeb_score = 500
	degree_exp = 5
	max_degree = 2
	score = 0
	category_name = 'questionAskedToMe'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if question_author_is_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - qauthor_degree_from_me))*qauthor_score
#		if me.is_celeb :
	return score

CATEGORIES['questionAskedToMe']['fun'] = calc_questionAskedToMe

def calc_answerOnMyQuestion(data,me=None):
	category_name = 'answerOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		return 1
	else:
		return 0

CATEGORIES['answerOnMyQuestion']['fun'] = calc_answerOnMyQuestion

def calc_commentOnMyQuestion(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'commentOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if comment_author_is_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - cauthor_degree_from_me))*cauthor_score
	return score

CATEGORIES['commentOnMyQuestion']['fun'] = calc_commentOnMyQuestion

def calc_commentsOnMyQuestion(data,me=None):
	celeb_scorer = [10,100,1000,10000,100000]
	normal_scorer = [1,5,10,20,50,100,200,500,1000]
	score = 0
	category_name = 'commentsOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['comments_now'] in scorer:
			score = 1
	return score

CATEGORIES['commentsOnMyQuestion']['fun'] = calc_commentsOnMyQuestion

def calc_viewsOnMyQuestion(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'viewsOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['views_now'] in scorer:
			score = 1
	return score

CATEGORIES['viewsOnMyQuestion']['fun'] = calc_viewsOnMyQuestion

def calc_upvoteOnMyQuestion(data,me=None):
	celeb_score = 500
	degree_exp = 5
	max_degree = 2
	score = 0
	category_name = 'upvoteOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if upvote_author_is_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - uauthor_degree_from_me))*uauthor_score
	return score

CATEGORIES['upvoteOnMyQuestion']['fun'] = calc_upvoteOnMyQuestion

def calc_upvotesOnMyQuestion(data,me=None):
	celeb_scorer = [10,100,1000,10000,100000]
	normal_scorer = [1,5,10,20,50,100,200,500,1000]
	score = 0
	category_name = 'upvotesOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['upvotes_now'] in scorer:
			score = 1
	return score

CATEGORIES['upvotesOnMyQuestion']['fun'] = calc_upvotesOnMyQuestion

def calc_commentOnMyAnswer(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'commentOnMyAnswer'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if comment_author_is_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - cauthor_degree_from_me))*cauthor_score
	return score

CATEGORIES['commentOnMyAnswer']['fun'] = calc_commentOnMyAnswer

def calc_commentsOnMyAnswer(data,me=None):
	celeb_scorer = [10,100,1000,10000,100000]
	normal_scorer = [1,5,10,20,50,100,200,500,1000]
	score = 0
	category_name = 'commentsOnMyAnswer'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['comments_now'] in scorer:
			score = 1
	return score

CATEGORIES['commentsOnMyAnswer']['fun'] = calc_commentsOnMyAnswer

def calc_viewsOnMyAnswer(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'viewsOnMyAnswer'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['views_now'] in scorer:
			score = 1
	return score

CATEGORIES['viewsOnMyAnswer']['fun'] = calc_viewsOnMyAnswer

def calc_viewsOnMyProfile(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'viewsOnMyProfile'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['views_now'] in scorer:
			score = 1
	return score

CATEGORIES['viewsOnMyProfile']['fun'] = calc_viewsOnMyProfile

def calc_followerOnMyProfile(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'followerOnMyProfile'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if follower_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - follower_degree))*follower_score
	return score

CATEGORIES['followerOnMyProfile']['fun'] = calc_followerOnMyProfile

def calc_followersOfMyProfile(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'followersOfMyProfile'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['followers_now'] in scorer:
			score = 1
	return score

CATEGORIES['followersOfMyProfile']['fun'] = calc_followersOfMyProfile

def calc_likeOnMyAnswer(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'likeOnMyAnswer'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if like_author_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - like_author_degree))*like_author_score
	return score

CATEGORIES['likeOnMyAnswer']['fun'] = calc_likeOnMyAnswer

def calc_likesOnMyAnswer(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'likesOnMyAnswer'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['likes_now'] in scorer:
			score = 1
	return score

CATEGORIES['likesOnMyAnswer']['fun'] = calc_likesOnMyAnswer

def calc_likeOnMyQuestion(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'likeOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if like_author_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - like_author_degree))*like_author_score
	return score

CATEGORIES['likeOnMyQuestion']['fun'] = calc_likeOnMyQuestion

def calc_likesOnMyQuestion(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'likesOnMyQuestion'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['likes_now'] in scorer:
			score = 1
	return score

CATEGORIES['likesOnMyQuestion']['fun'] = calc_likesOnMyQuestion

def calc_upvoteOnQuestionToMe(data,me=None):
	celeb_score = 500
	degree_exp = 3
	max_degree = 2
	score = 0
	category_name = 'upvoteOnQuestionToMe'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if upvote_author_is_celeb:
			score += celeb_score
		score += (degree_exp ** (max_degree - uauthor_degree_from_me))*uauthor_score
	return score

CATEGORIES['upvoteOnQuestionToMe']['fun'] = calc_upvoteOnQuestionToMe

def calc_upvotesOnQuestionToMe(data,me=None):
	celeb_scorer = [1000,10000,100000,1000000]
	normal_scorer = [100,200,500,1000,50000,100000,1000000]
	score = 0
	category_name = 'upvotesOnQuestionToMe'
	if validate(data,CATEGORIES[category_name]['info'],category_name,me):
		if me.is_celeb:
			scorer = celeb_scorer
		else:
			scorer = normal_scorer
		if data['upvotes_now'] in scorer:
			score = 1
	return score

CATEGORIES['upvotesOnQuestionToMe']['fun'] = calc_upvotesOnQuestionToMe