import mailconfig
import boto.ses
import sys

from configs import config
from raygun4py import raygunprovider
from models import Email,BadEmail,Email
from app import db
import datetime

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)


class SimpleMailer(object):
    """
    Class defining the simple mailer
    """
    def __init__(self,sender, key=mailconfig.aws_access_key_id,secret_key=mailconfig.aws_secret_access_key, region='us-east-1'):
        """
        Initializes the SES connection and sets up the sender mail ID
        """
        self.sender_id = sender
        self.conn = boto.ses.connect_to_region(region,aws_access_key_id=key, aws_secret_access_key=secret_key)

    def send_mail(self, recipients, message_subject, message_body, user='code'):
        """
        Send an HTML E-Mail
        """
        if type(recipients) in [type(''), type(u'')]:
            recipients = [recipients]

        email = Email(user, self.sender_id, message_subject, message_body, datetime.datetime.now())
        db.session.add(email)
        db.session.commit()
    
        for recipient in recipients:
            try:
                if BadEmail.query.filter(BadEmail.email==recipient).first():
                    return
                self.conn.send_email(self.sender_id, message_subject, message_body, recipient, format='html')
                
                new_email_sent = EmailSent(self.sender_id, recipient, email_id, datetime.datetime.now())
                db.session.add(new_email_sent)
                db.session.commit()
            except Exception as e:
                err = sys.exc_info()
                raygun.send(err[0],err[1],err[2])