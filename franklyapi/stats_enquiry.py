from app import db
import models
from sqlalchemy import text
from  stats_mail_writer import make_html_table

#============================================
#             twice a day enquiry
#============================================

def new_registrations(show_celeb=True, show_non_celeb=True, since_hours = 12):
	results = db.session.execute(text("""SELECT u.user_type, u.registered_with, count(u.username)
											from users u  
											where u.user_since > now() - interval :since_hours hour
											and u.monkness = -1
											group by u.user_type, u.registered_with;"""),
										params={'since_hours':since_hours}
								)
								
	resp = make_html_table(results)
	return resp

def count_of_question_asked(show_celeb=True, show_non_celeb=True, since_hours = 12):
	results = db.session.execute(text("""SELECT u.user_type , count(q.id)
											from users u 
											inner join questions q on q.question_to = u.id
											where u.monkness = -1
											and q.deleted = false
											and q.timestamp > now() - interval 12 hour;""")
								)
								
	resp = make_html_table(results)
	return resp

def videos_uploaded():
	results = db.session.execute(text("""SELECT v.username, v.url ,u.user_type
											from videos v
											inner join users u on v.username = u.username
											left join testers t on v.username = t.username
											where u.monkness = -1
											and t.id IS NULL
											and v.delete = false
											and v.created_at > now() - interval 12 hour;""")
								)
								
	resp = make_html_table(results)
	return resp

#============================================
#             daily enquiry
#============================================

def users_asking_questions_more_than_or_equal_to(count=3):
	results = db.session.execute(text("""SELECT u.first_name as'Name' ,u.username, u.email, u.phone_num as 'Phone'
											from users u  
											inner join questions q on u.id = q.question_author 
											left join testers t on u.username = t.username
											where q.timestamp > now() - interval 1 day
											and t.id IS NULL
											and u.monkness = -1
											group by u.id having count(1) >= :count;"""),
										params={'count':count}
								)
								
	resp = make_html_table(results)
	return resp

def users_being_asked_questions_more_than_or_equal_to(count=3):
	results = db.session.execute(text("""SELECT u.first_name as'Name' ,u.username, u.email, u.phone_num as 'Phone' 
											from users u 
											inner join questions q on u.id = q.question_to 
											left join testers t on u.username = t.username
											where q.timestamp > now() - interval 1 day
											and t.id IS NULL
											and u.monkness = -1
											group by u.id having count(1) >= :count"""),
										params={'count':count}
								)
								
	resp = make_html_table(results)
	return resp	

def questions_with_most_upvotes(count=20):
	results = db.session.execute(text("""SELECT u.first_name as 'Asked to', u.username as 'username', concat('http://www.frankly.me/',u.username,'/',q.slug)  as question_link 
											from questions q 
											inner join question_upvotes qu on q.id = qu.question 
											inner join users umonk on qu.user = umonk.id
											inner join users u on u.id = q.question_to
											left join testers t on u.username = t.username
											where umonk.monkness = -1
											and t.id IS NULL
											and qu.downvoted = false
											group by q.id 
											order by count(1) desc 
											limit :limit"""),
										params={'limit':count}
								)
								
	resp = make_html_table(results)
	return resp

def users_with_highest_increase_in_follows(count=20):
	results = db.session.execute(text("""SELECT u.first_name as'Name' ,u.username, u.email, u.phone_num as 'Phone'
											from users u
											inner join user_follows uf on u.id = uf.followed
											inner join users umonk on uf.user = umonk.id
											left join testers t on u.username = t.username
											where umonk.monkness = -1
											and t.id IS NULL
											and u.monkness = -1
											and uf.timestamp >= now() -interval 1 day
											and uf.unfollowed = false
											group by u.id
											order by count(1) desc
											limit :count"""),
										params={'count':count}
								)
								
	resp = make_html_table(results)
	return resp

def questions_with_highest_likes(count=20):
	results = db.session.execute(text("""SELECT u.first_name as 'Asked to', u.username as 'username', concat('http://www.frankly.me/',u.username,'/',q.slug)  as question_link , count(1) as 'No. of Likes'
											from questions q
											inner join posts p on q.id = p.question
											inner join post_likes pl on p.id = pl.post
											inner join users umonk on pl.user = umonk.id
											inner join users u on u.id = q.question_to
											left join testers t on u.username = t.username
											where umonk.monkness = -1
											and t.id IS NULL
											and pl.unliked = false and p.deleted = false
											group by q.id
											order by count(1) desc
											limit :count ;"""),
										params={'count':count}
								)
								
	resp = make_html_table(results)
	return resp

def questions_with_highest_comments(count=20):
	results = db.session.execute(text("""SELECT u.first_name as 'Asked to', u.username as 'username', concat('http://www.frankly.me/',u.username,'/',q.slug)  as question_link , count(1) as 'No. of Comments'
											from questions q
											inner join posts p on q.id = p.question
											inner join comments c on p.id = c.on_post
											inner join users umonk on c.comment_author = umonk.id
											inner join users u on u.id = q.question_to
											left join testers t on u.username = t.username
											where umonk.monkness = -1
											and t.id IS NULL
											and c.deleted = false and p.deleted = false
											group by q.id
											order by count(1) desc
											limit :count ;"""),
										params={'count':count}
								)
								
	resp = make_html_table(results)
	return resp
	