from models import *
import datetime
import PyRSS2Gen
from app import db
from sqlalchemy.sql import text

def generate_answers_rss(count=30,filename='/tmp/franklymeanswers.xml'):
	rssitems = []
	#answers = Post.query.filter(Post.deleted==False).order_by(Post.timestamp.desc()).limit(count).all()
	answers = db.session.execute(text("""SELECT posts.id, questions.body,
										a.first_name as answer_author,b.first_name as question_author,
                                        posts.media_url, posts.answer_type, posts.timestamp
                                        FROM posts INNER JOIN users a ON a.id = posts.answer_author
                                        INNER JOIN questions ON questions.id = posts.question
                                        INNER JOIN users b ON b.id = posts.question_author
                                        WHERE posts.deleted=false
                                        ORDER BY posts.timestamp DESC LIMIT :limit"""),
                                    params = {'limit':count}
                                )
	for answer in answers:
		rssitems.append(PyRSS2Gen.RSSItem(
			title ='New answer by %s' % answer.answer_author,
			link = answer.media_url,
			description= '%s answered to "%s" ~ asked by %s' % (answer.answer_author,answer.body,answer.question_author),
			pubDate=answer.timestamp
			))
	rss = PyRSS2Gen.RSS2(
		title='Frankly.me',
		link='www.frankly.me',
		description='New answers on frankly.me',
		items = rssitems
		)
	rss.write_xml(open(filename,'w'))