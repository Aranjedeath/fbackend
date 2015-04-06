from jinja2 import Environment, PackageLoader
from infra import SimpleMailer
from models import MailLog
from app import db
from configs import config
from helper import *

import datetime
import helper
import os

env = Environment(loader=PackageLoader('mail', 'mail_templates'))

header_template = env.get_template('style_zero.html')

mail_sender = SimpleMailer(config.FROM_EMAIL_ADDRESS)


def mail(email_id, object_id = None, mail_type="", subject="", body="",
         cutoff_time=datetime.timedelta(days=1), mail_limit=1):
    '''
     For any kind of email there is a cut off time with which
     it can be sent again. The number of such mails can also
     be passed as a parameter.
     Ex: Question asked email can only be sent twice in a 3 day period
    '''
    if object_id:

        now = datetime.datetime.now()
        if MailLog.query.filter(MailLog.email_id == email_id, MailLog.object_id == object_id,
                                MailLog.mail_type == mail_type,
                                MailLog.created_at > (now - cutoff_time)).count() < mail_limit:

            mail_sender.send_mail(email_id, subject, body)
            log_mail(email_id=email_id, mail_type=mail_type, object_id=object_id)



def log_mail(email_id, mail_type, object_id):
    log = MailLog(email_id=email_id, mail_type=mail_type, object_id=object_id)
    db.session.add(log)
    db.session.commit()


def welcome_mail(receiver_email, receiver_name,
                 receiver_username, receiver_password, user_id, mail_type="welcome-mail"):

    cutoff_time = datetime.timedelta(days=1000)
    mail_dict['salutation'] = "Hi %s" % receiver_name
    mail_dict['email_text'] = helper.dict[mail_type]['body'] % (receiver_username, receiver_password)

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time= cutoff_time, mail_limit = 1)


def forgot_password(receiver_email, token, receiver_name, user_id, mail_type="forgot_password"):
    url = os.path.join(config.WEB_URL, 'reset-password?token={token}'.format(token=token))

    cutoff_time = datetime.timedelta(hours=1)
    mail_dict['salutation'] = "Hi {receiver_name}".format(receiver_name=str(receiver_name))
    mail_dict['email_text'] = helper.dict[mail_type]['body'].format(reset_password_link=url)

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time=cutoff_time, mail_limit=3)


def question_asked(receiver_email, receiver_name, question_to_name, is_first,
                   question_id, mail_type="question_asked"):

    cutoff_time = datetime.timedelta(days=3)

    mail_dict['salutation'] = "Hi %s" % receiver_name
    mail_dict['email_text'] = helper.dict[mail_type]['body'] % question_to_name

    if is_first:
        mail_dict['email_text'] = helper.dict[mail_type]['body_first_question']

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=question_id,
         cutoff_time=cutoff_time, mail_limit=1)


def question_answered(receiver_email, receiver_name, celebrity_name, question, web_link,
                      post_id, mail_type='post_add'):

    cutoff_time = datetime.timedelta(days=10000)

    mail_dict['salutation'] = "Hi %s" % receiver_name
    mail_dict['email_text'] = helper.dict['question_answered']['body'] % (celebrity_name, web_link, question)

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=post_id,
         cutoff_time=cutoff_time, mail_limit=1)


#Weekly Email
def inactive_profile(receiver_email, receiver_name):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = helper.dict['inactive_profile']['body']

    mail_sender.send_mail(receiver_email,
                          helper.dict['inactive_profile']['subject'],
                          header_template.render(render_dict))

