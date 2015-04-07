from jinja2 import Environment, PackageLoader
from infra import SimpleMailer
from models import MailLog, User, AccessToken, Question
from notification import push_notification as push
from app import db
from configs import config
from helper import *
from CustomExceptions import ObjectNotFoundException

import datetime
import helper
import os

env = Environment(loader=PackageLoader('mail', 'mail_templates'))

header_template = env.get_template('style_zero.html')

mail_sender = SimpleMailer()

# TODO Add option to unsubscribe in the email

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

# TODO Testing and sending login link instead of password
def welcome_mail(receiver_email, receiver_name,
                 receiver_username, receiver_password, user_id, mail_type="welcome-mail"):

    cutoff_time = datetime.timedelta(days=1000)
    mail_dict['salutation'] = "Hi %s" % receiver_name
    mail_dict['email_text'] = helper.dict[mail_type]['body'] % (receiver_username, receiver_password)

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time= cutoff_time, mail_limit = 1)

# TODO Testing
def forgot_password(receiver_email, token, receiver_name, user_id, mail_type="forgot_password"):
    url = os.path.join(config.WEB_URL, 'reset-password?token={token}'.format(token=token))

    cutoff_time = datetime.timedelta(hours=1)
    mail_dict['salutation'] = "Hi {receiver_name}".format(receiver_name=str(receiver_name))
    mail_dict['email_text'] = helper.dict[mail_type]['body'].format(reset_password_link=url)

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time=cutoff_time, mail_limit=3)

# TODO Testing
def question_asked(question_to, question_from, question_id, question_body,
                   from_widget=False, mail_type="question_asked"):

    users = User.query.filter(User.id.in_([question_from,question_to]))

    for user in users:
        if user.id == question_from:
            asker = user
        if user.id == question_to:
            asked = user

    cutoff_time = datetime.timedelta(days=3)

    ''' If asker source is widget
        and does not have any active mobile devices
        then send them an email notification
        confirming that the question has been asked
    '''
    #from_widget and not
    if len(push.get_active_mobile_devices(asker.id)):

        is_first = True if Question.query.filter(Question.question_author == asker.id).count() == 1 else False

        mail_type += "_by"
        mail_dict['salutation'] = "Hi %s" % asker.first_name
        mail_dict['email_text'] = helper.dict[mail_type]['body'] % asked.first_name

        if is_first:
            mail_dict['email_text'] = helper.dict[mail_type]['body_first_question']

        mail(email_id=asker.email, subject=helper.dict[mail_type]['subject'],
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=question_id,
             cutoff_time=cutoff_time, mail_limit=1)

    if len(push.get_active_mobile_devices(asked.id)):

        mail_type += "_to"
        mail_dict['salutation'] = "Hi %s" % asked.first_name
        mail_dict['email_text'] = helper.dict[mail_type]['body'] % (asked.first_name, question_body)

        mail(email_id=asker.email, subject=helper.dict[mail_type]['subject'],
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=question_id,
             cutoff_time=cutoff_time, mail_limit=1)

# TODO Testing
def question_answered(receiver_email, receiver_name, celebrity_name, question, web_link,
                      post_id, user_id, mail_type='post_add'):

    if not len(push.get_active_mobile_devices(user_id)):
        cutoff_time = datetime.timedelta(days=10000)

        mail_dict['salutation'] = "Hi %s" % receiver_name
        mail_dict['email_text'] = helper.dict['question_answered']['body'] % (celebrity_name, web_link, question)

        mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=post_id,
             cutoff_time=cutoff_time, mail_limit=1)

# TODO Method which would call this
def inactive_profile(receiver_email, receiver_name, user_id, mail_type="inactive_profile"):

    cutoff_time = datetime.timedelta(days=30)
    mail_dict['salutation'] = "Hi %s" % receiver_name
    mail_dict['email_text'] = helper.dict[mail_type]['body']

    mail(email_id=receiver_email, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time=cutoff_time, mail_limit=1)

# TODO Email content
def new_celebrity_profile(for_users, celebrity_id, mail_type="new_celebrity"):

    cutoff_time = datetime.timedelta(days=100)
    try:
        celebrity = User.query.filter(User.id == celebrity_id).first()

        for user in for_users:
            u = User.query.filter(User.id == user).first()

            mail_dict['salutation'] = "Hi %s" % u.first_name
            mail_dict['email_text'] = helper.dict[mail_type]['body']

            mail(email_id=u.email, subject=helper.dict[mail_type]['subject'],
                 body=header_template.render(mail_dict), mail_type = (mail_type + "_" + celebrity.username),
                 object_id=user, cutoff_time=cutoff_time, mail_limit=1)

    except ObjectNotFoundException:
        pass

# TODO Email content
def weekly_digest(for_users, mail_type="weekly_digest"):
    cutoff_time = datetime.timedelta(days=7)
    try:

        for user in for_users:
            u = User.query.filter(User.id == user).first()

            mail_dict['salutation'] = "Hi %s" % u.first_name
            mail_dict['email_text'] = helper.dict[mail_type]['body']

            mail(email_id=u.email, subject=helper.dict[mail_type]['subject'],
                 body=header_template.render(mail_dict), mail_type = mail_type,
                 object_id=user, cutoff_time=cutoff_time, mail_limit=1)

    except ObjectNotFoundException:
        pass