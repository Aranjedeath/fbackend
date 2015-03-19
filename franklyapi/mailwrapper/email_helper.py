from jinja2 import Environment, PackageLoader
from kabootar import SimpleMailer
import mail_content


env = Environment(loader = PackageLoader('mailwrapper','mail_templates'))

header_template = env.get_template('standard_email.html')

team_signature = "Lots of love, <br/> Frankly.me Team"
personal_signature = "Malvika, <br/> Community Manager <br/> Frankly.me"

render_dict = {
    "logo_target_url": "http://frankly.me",
    "logo_image_url": "http://frankly.me/images/icons/logoTrimmedOrange.png",
    "company_name": "Frankly.me"
}

mail_sender = SimpleMailer('Frankly@frankly.me')


def welcome_mail(receiver_email,receiver_name,receiver_username,receiver_password):

    render_dict['salutation'] = mail_content.dict['welcome_mail']['salutation'] % receiver_name
    render_dict['email_text'] = mail_content.dict['welcome_mail']['body'] % (receiver_username, receiver_password)
    render_dict['signature'] = personal_signature
    mail_sender.send_mail(receiver_email, mail_content.dict['welcome_mail']['subject'],
                          header_template.render(render_dict))


def first_question_asked(receiver_email,receiver_name):
    render_dict['salutation'] = mail_content.dict['welcome_mail']['salutation'] % receiver_name
    render_dict['email_text'] = mail_content.dict['first_question']['body']
    render_dict['signature'] = personal_signature
    mail_sender.send_mail(receiver_email,mail_content.dict['first_question']['subject'],
                          header_template.render(render_dict))


def question_asked(receiver_email,celebrity_name,other_celebs):




def send_weekly_report(receiver_emails,report):
    for email in receiver_emails:
        mail_sender.send_mail(email,"Weekly Report",report)



# def question_asked(receiver_email,celebrity_name,other_celebs):
#     #TODO Setup Body
#     mail_sender.send_mail(receiver_email,mail_dict['question_asked']['subject'],None)
#
# # def question_answered(receiver_email,receiver_name,celebrity_name,link_to_answer,hyper):
# #     #TODO Setup Body
# #     if hyper:
# #         # TO
# #         #
# #         #
# #         # DO Do Something
# #         # DO Do Something
# #     else:
# #         pass
# #     mail_sender.send_mail(receiver_email)
#
#
# def inactive_profile(receiver_email,receiver_name):
#     #TODO kar lo kuch
def send_mail_for_sapru(receiver_email,receiver_name,link):
    render_dict['salutation'] = "Hi %s" % receiver_name
    render_dict['email_text'] = mail_content.dict['sapru']['body'] % link
    render_dict['signature']  = personal_signature
    mail_sender.send_mail(receiver_email,mail_content.dict['sapru']['subject'],
                          header_template.render(render_dict))