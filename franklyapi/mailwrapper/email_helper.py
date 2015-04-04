from jinja2 import Environment, PackageLoader
from kabootar import SimpleMailer
from models import MailLog
from app import db
import mail_content


from configs import config
import os



env = Environment(loader=PackageLoader('mailwrapper', 'mail_templates'))

header_template = env.get_template('standard_email.html')

team_signature = "Lots of love, <br/> Frankly.me Team"
personal_signature = "Pallavi, <br/> Community Manager <br/> Frankly.me"

render_dict = {
    "logo_target_url": "http://frankly.me",
    "logo_image_url": "http://frankly.me/images/icons/logoTrimmedOrange.png",
    "company_name": "Frankly.me",
    "signature": personal_signature
}

mail_sender = SimpleMailer('Frankly@franklymail.com')


def welcome_mail(receiver_email, receiver_name,
    receiver_username, receiver_password):

    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['welcome_mail']['body'] % (receiver_username, receiver_password)

    mail_sender.send_mail(receiver_email, mail_content.dict['welcome_mail']['subject'],
                          header_template.render(render_dict))


def forgot_password(receiver_email, token, reciever_name):
    url = os.path.join(config.WEB_URL,
            'reset-password?token={token}'.format(token=token))


    render_dict['salutation'] = "Hi {reciever_name}".format(
            reciever_name=str(reciever_name))
    render_dict['email_text'] = mail_content.dict['forgot_password']['body'].format(
            reset_password_link=url)


    mail_sender.send_mail(receiver_email,
                          mail_content.dict['forgot_password']['subject'],
                          header_template.render(render_dict))



def question_asked(receiver_email, receiver_name, question_to_name, is_first):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['question_asked']['body'] % question_to_name
    if is_first:
        render_dict['email_text'] = mail_content.dict['question_asked']['body_first_question']

    mail_sender.send_mail(receiver_email,
                          mail_content.dict['question_asked']['subject'],
                          header_template.render(render_dict))


def question_answered(receiver_email, receiver_name, celebrity_name, question, web_link,
                      post_id, mail_type='post-add'):

    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['question_answered']['body'] % (celebrity_name, web_link, question)

    if MailLog.query.filter(MailLog.email_id == receiver_email, MailLog.object_id == post_id,
                            MailLog.mail_type == mail_type).count() == 0:
        print 'sending mail'
        mail_sender.send_mail(receiver_email,
                              mail_content.dict['question_answered']['subject'],
                              header_template.render(render_dict))
        log = MailLog(email_id=receiver_email, mail_type=mail_type, object_id=post_id)
        db.session.add(log)
        db.session.commit()

#Weekly Email
def inactive_profile(receiver_email, receiver_name):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['inactive_profile']['body']

    mail_sender.send_mail(receiver_email,
                          mail_content.dict['inactive_profile']['subject'],
                          header_template.render(render_dict))


def send_weekly_report(recipients, report):
    mail_sender.send_mail(recipients, "Weekly Report", report)


def content_report(recipients, subject, report):
    mail_sender.send_mail(recipients, subject, report)


def cron_job_update(cron_type="Dhak Dhak", message='Keep running!'):
    mail_sender.send_mail(config.DEV_EMAILS, cron_type, message)


def send_mail_for_sapru(receiver_email, receiver_name, link):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['sapru']['body'] % link
    render_dict['signature']  = personal_signature
    mail_sender.send_mail(receiver_email,
                          mail_content.dict['sapru']['subject'],
                          header_template.render(render_dict))


def push_stats(body):
    mail_sender.send_mail(['varun@frankly.me','abhishek@frankly.me','nikunj@frankly.me'],
                           'Push Notification Stats',
                          body)