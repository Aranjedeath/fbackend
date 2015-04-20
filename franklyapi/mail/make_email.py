from jinja2 import Environment, PackageLoader
from infra import SimpleMailer
from models import MailLog, User, Question
from CustomExceptions import ObjectNotFoundException
from helper import *
from app import db

import util
import datetime
import helper
import os

env = Environment(loader=PackageLoader('mail', 'mail_templates'))

header_template = env.get_template('style_zero.html')

mail_sender = SimpleMailer()

# TODO Change link to un-subscribe
# TODO Content for inactive profile
# TODO Email content for new celeb email and for news digest - CONTENT TEAM
def mail(email_id, log_id, object_id = None, mail_type="", subject="", body="",
         cutoff_time=datetime.timedelta(days=1), mail_limit=1):
    '''
     For any kind of email there is a cut off time with which
     it can be sent again. The number of such mails can also
     be passed as a parameter.
     Ex: Question asked email can only be sent twice in a 3 day period
    '''
    if object_id:

        now = datetime.datetime.now()
        count_of_email_sent = MailLog.query.filter(MailLog.email_id == email_id, MailLog.object_id == object_id,
                                 MailLog.mail_type == mail_type,
                                 MailLog.created_at > (now - cutoff_time)).count()
        if count_of_email_sent <= mail_limit:
                mail_sender.send_mail(email_id, subject, body, log_id)


def log_mail(email_id, mail_type, object_id):
    log = MailLog(email_id=email_id, mail_type=mail_type, object_id=object_id)
    db.session.add(log)
    db.session.commit()
    return log.id


def welcome_mail(user_id, mail_type="welcome_mail"):

    user = User.query.filter(User.id  == user_id).first()
    cutoff_time = datetime.timedelta(days=1000)
    log_id = log_mail(user.email, mail_type, user_id)
    mail_dict['salutation'] = "Hi %s" % user.first_name
    mail_dict['email_text'] = helper.dict[mail_type]['body'].format(user.username)
    mail_dict['pixel_image_url'] += "?id=" + log_id
    print log_id

    mail(email_id=user.email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time= cutoff_time, mail_limit = 1)


def forgot_password(receiver_email, token, receiver_name, user_id, mail_type="forgot_password"):

    url = os.path.join(config.WEB_URL, 'reset-password?token={token}'.format(token=token))
    cutoff_time = datetime.timedelta(hours=1)
    log_id =log_mail(receiver_email, mail_type, user_id)

    mail_dict['salutation'] = "Hi {receiver_name}".format(receiver_name=str(receiver_name))
    mail_dict['email_text'] = helper.dict[mail_type]['body'].format(reset_password_link=url)
    mail_dict['pixel_image_url'] += "?id=" + log_id

    mail(email_id=receiver_email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user_id,
         cutoff_time=cutoff_time, mail_limit=3)


def question_asked(question_id,
                   from_widget=False, mail_type="question_asked"):

    question = Question.query.filter(Question.id == question_id).first()
    users = User.query.filter(User.id.in_([question.question_author, question.question_to]))

    for user in users:
        if user.id == question.question_author:
            asker = user
        if user.id == question.question_to:
            asked = user

    cutoff_time = datetime.timedelta(days=3)

    ''' If asker source is widget
        and does not have any active mobile devices
        then send them an email notification
        confirming that the question has been asked
    '''
#and not len(notification_util.get_active_mobile_devices(asker.id))
    if from_widget :

        #is_first = True if Question.query.filter(Question.question_author == asker.id).count() == 1 else False
        mail_type += "_by"
        mail_dict['email_text'] = helper.dict[mail_type]['body'].format(asker.first_name, asked.first_name,
                                                                    asked.first_name.split(" ")[0])

        # if is_first:
        #     mail_dict['email_text'] = helper.dict[mail_type]['body_first_question']

        log_id = log_mail(asker.email, mail_type, question_id)

        mail_dict['salutation'] = "Hi %s" % asker.first_name
        mail_dict['pixel_image_url'] += "?id=" + log_id

        mail(email_id=asker.email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=question_id,
             cutoff_time=cutoff_time, mail_limit=1)
        mail_type = "question_asked"


    if not len(util.get_active_mobile_devices(asked.id)):

        mail_type += "_to"
        subject = helper.dict[mail_type]['subject'] % asker.first_name
        log_id = log_mail(asked.email, mail_type, question_id)

        print question.slug
        question_url = (config.WEB_URL + "/{0}/{1}").format(asked.username, question.slug)
        mail_dict['salutation'] = "Hi %s" % asked.first_name
        mail_dict['email_text'] = helper.dict[mail_type]['body'].format(asker.first_name, question_url, question.body)
        mail_dict['pixel_image_url'] += "?id=" + log_id

        mail(email_id=asked.email, log_id=log_id, subject=subject,
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=question_id,
             cutoff_time=cutoff_time, mail_limit=1)


def question_answered(receiver_email, receiver_name, celebrity_name, question, web_link,
                      post_id, user_id, mail_type='post_add'):

    if len(util.get_active_mobile_devices(user_id)):
        cutoff_time = datetime.timedelta(days=10000)

        log_id = log_mail(receiver_email, mail_type, post_id)
        mail_dict['salutation'] = "Hi %s" % receiver_name
        mail_dict['email_text'] = helper.dict[mail_type]['body'] % (celebrity_name, web_link, question)
        mail_dict['pixel_image_url'] += "?id=" + log_id

        mail(email_id=receiver_email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
             body=header_template.render(mail_dict), mail_type=mail_type, object_id=post_id,
             cutoff_time=cutoff_time, mail_limit=1)


def inactive_profile(user_id, mail_type="inactive_profile"):

    user = User.query.filter(User.id == user_id).first()
    cutoff_time = datetime.timedelta(days=30)
    log_id = log_mail(user.email, mail_type, user.id)

    mail_dict['salutation'] = "Hi %s" % user.first_name
    mail_dict['email_text'] = helper.dict[mail_type]['body']
    mail_dict['pixel_image_url'] += "?id=" + log_id

    mail(email_id=user.email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
         body=header_template.render(mail_dict), mail_type=mail_type, object_id=user.id,
         cutoff_time=cutoff_time, mail_limit=1)


def new_celebrity_profile(for_users, celebrity_id, mail_type="new_celebrity"):

    cutoff_time = datetime.timedelta(days=100)
    try:
        celebrity = User.query.filter(User.id == celebrity_id).first()

        for user in for_users:
            u = User.query.filter(User.id == user).first()

            log_id = log_mail(user.email, mail_type, celebrity_id)
            mail_dict['salutation'] = "Hi %s" % u.first_name
            mail_dict['email_text'] = helper.dict[mail_type]['body']
            mail_dict['pixel_image_url'] += "?id=" + log_id

            mail(email_id=u.email, log_id=log_id, subject=helper.dict[mail_type]['subject'],
                 body=header_template.render(mail_dict), mail_type = (mail_type + "_" + celebrity.username),
                 object_id=user, cutoff_time=cutoff_time, mail_limit=1)

    except ObjectNotFoundException:
        pass


def weekly_digest(for_users, subject, mail_type="weekly_digest"):
    cutoff_time = datetime.timedelta(days=7)
    try:

        for user in for_users:
            u = User.query.filter(User.id == user).first()
            log_id = log_mail(u.email, mail_type, u.id)
            body = "TODO"
            mail_dict['pixel_image_url'] += "?id=" + log_id
            mail(email_id=u.email, log_id=log_id, subject=subject,
                 body=body, mail_type = mail_type,
                 object_id=user.id, cutoff_time=cutoff_time, mail_limit=1)

    except ObjectNotFoundException:
        pass


def inactive_users(users):
    from sqlalchemy import desc
    from models import Like, Follow, Upvote, Question
    now = datetime.datetime.now()
    time_span = now - datetime.timedelta(days=7)
    for u in users:
        last_like = Like.query.filter(Like.user
                                      == u.id).order_by(desc(Like.timestamp)).first().timestamp < time_span
        last_upvote = Follow.query.filter(Upvote.user
                                          == u.id).order_by(desc(Upvote.timestamp)).first().timestamp < time_span
        last_follow = Follow.query.filter(Follow.user
                                          == u.id).order_by(desc(Follow.timestamp)).first().timestamp < time_span

        last_question= Question.query.filter(Question.question_author ==
                                             u.id).order_by(desc(Question.timestamp)).first().timestamp < time_span

        if last_like or last_follow or last_upvote or last_question:
            pass
        else:
            inactive_profile(u.id)


def test():
    user = User.query.filter(User.username == 'chimpspanner').first()
    log_id = log_mail('varunj.dce@gmail.com',"mail_type_test", user.id)
    mail_dict['email_text'] = "Testing testing"
    mail_dict['pixel_image_url'] = config.PIXEL_IMAGE_ENDPOINT + "?id=" + log_id
    print mail_dict['pixel_image_url']

    mail(email_id=user.email, log_id=log_id, subject="Testing",
         body=header_template.render(mail_dict), mail_type="mail_type_test", object_id=user.id,
         cutoff_time= datetime.timedelta(seconds=1), mail_limit = 1000)