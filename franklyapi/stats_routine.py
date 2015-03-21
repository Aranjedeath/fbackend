import datetime
from stats_enquiry import *
from stats_mail_writer import *
from mailwrapper import email_helper
#SES_EMAIL = 'goelrishabh09@gmail.com'

mail_sender = email_helper.SimpleMailer('Frankly@frankly.me')

receipent = 'goelrishabh09@gmail.com'
#receipent = 'swati@frankly.me'

def daily_mail():
	
	msg1 = make_panel('Usernames of people asking 3 or more questions',
		users_asking_questions_more_than_or_equal_to(3)) 
	
	msg2 = make_panel('Usernames of people who have been asked 3 or more questions',
		users_being_asked_questions_more_than_or_equal_to(3))
	
	msg3 = make_panel('Links of top 20 questions with the most (real) upvotes',
		questions_with_most_upvotes(20)) 
	
	msg4 = make_panel('Usernames of top 20 people with the highest increase in follows (real follows)',
		users_with_highest_increase_in_follows(20))
	
	msg5 = make_panel('Links of top 20 questions with the highest likes (real)',
		questions_with_highest_likes(20)) 
	
	msg6= make_panel('Links of top 20 questions with the highest comments (real)',
		questions_with_highest_comments(20))
	
	msg = add_style() + msg1 + msg2 + msg3 + msg4 + msg5 + msg6
	
	mail_sender.send_mail(receipent,'Daily Report',msg);
	# result = controllers.create_email('routine',SES_EMAIL,'Daily updates',msg);
	
	# print controllers.send_email('routine',result['id'],SES_EMAIL,receipent,datetime.datetime.now())

def twice_a_day_mail():
	
	msg1 = make_panel('New registrations (celeb and non-celeb) in last 12 hours  Source & number of registrations',
		new_registrations()) 
	
	msg2 = make_panel('No. of questions asked (excluding those from the dashboard)',
		count_of_question_asked())
	
	msg3 = make_panel('Videos uploaded   (celeb and non-celeb) with link',
		videos_uploaded())
	
	msg = add_style() + msg1 + msg2 + msg3
	
	mail_sender.send_mail(receipent,'Twice a day Report',msg);

	# result = controllers.create_email('routine',config.SES_EMAIL,'Twice a day updates',msg);
	
	# print controllers.send_email('routine',result['id'],config.SES_EMAIL,receipent,datetime.datetime.now())