from jinja2 import Environment, PackageLoader
from kabootar import SimpleMailer
import mail_content


env = Environment(loader = PackageLoader('mailwrapper','mail_templates'))

header_template = env.get_template('standard_email.html')

team_signature = "Lots of love, <br/> Frankly.me Team"
personal_signature = "Pallavi, <br/> Community Manager <br/> Frankly.me"

render_dict = {
    "logo_target_url": "http://frankly.me",
    "logo_image_url": "http://frankly.me/images/icons/logoTrimmedOrange.png",
    "company_name": "Frankly.me",
    "signature": personal_signature
}

mail_sender = SimpleMailer('Frankly@frankly.me')


def welcome_mail(receiver_email,receiver_name,receiver_username,receiver_password):

    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['welcome_mail']['body'] % (receiver_username, receiver_password)

    mail_sender.send_mail(receiver_email, mail_content.dict['welcome_mail']['subject'],
                          header_template.render(render_dict))


def forgot_password(receiver_email):

    render_dict['salutation'] = "Hi,"
    render_dict['email_text'] = "Forgot password:"

    mail_sender.send_mail(receiver_email, mail_content.dict['forgot_password']['subject'],
                          header_template.render(render_dict))



def question_asked(receiver_email, receiver_name, celebrity_name, is_first):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['question_asked']['body'] % celebrity_name
    if is_first:
        render_dict['email_text'] = mail_content.dict['question_asked']['body_first_question']

    mail_sender.send_mail(receiver_email,mail_content.dict['question_asked']['subject'],
                          header_template.render(render_dict))

def question_answered(receiver_email, receiver_name, celebrity_name, question):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['question_answered']['body'] % (celebrity_name, question)

    mail_sender.send_mail(receiver_email, mail_content.dict['question_answered']['subject'],
                          header_template.render(render_dict))

#Weekly Email
def inactive_profile(receiver_email,receiver_name):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['inactive_profile']['body']

    mail_sender.send_mail(receiver_email ,mail_content.dict['inactive_profile']['subject'],
                          header_template.render(render_dict))


def send_weekly_report(recipients,report):
    mail_sender.send_mail(recipients, "Weekly Report", report)


def content_report(recipients, subject, report):
    mail_sender.send_mail(recipients, subject, report)


def cron_job_failed(cron_type):
    mail_content.send_mail(['varun@frankly.me','shashank@frankly.me','nikhil@frankly,me'], cron_type +
                           " Job failed", "Please check")


def send_mail_for_sapru(receiver_email,receiver_name,link):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['sapru']['body'] % link
    render_dict['signature']  = personal_signature
    mail_sender.send_mail(receiver_email,mail_content.dict['sapru']['subject'],
                          header_template.render(render_dict))