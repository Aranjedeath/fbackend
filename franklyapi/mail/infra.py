from configs import config
from raygun4py import raygunprovider
from models import Email, BadEmail, EmailSent
from app import db

import boto.ses
import sys
import datetime

raygun = raygunprovider.RaygunSender(config.RAYGUN_KEY)


class SimpleMailer(object):
    """
    Class defining the simple mailer
    """
    def __init__(self, sender = None, key=config.AWS_KEY, secret_key=config.AWS_SECRET, region=config.AWS_REGION):
        """
        Initializes the SES connection and sets up the sender mail ID
        """

        self.sender_id = sender if sender else config.FROM_EMAIL_ADDRESS
        try:
            self.conn = boto.ses.connect_to_region(region, aws_access_key_id=key, aws_secret_access_key=secret_key)
        except Exception as e:
            err = sys.exc_info()
            raygun.send(err[0], err[1], err[2])

    def send_mail(self, recipients, message_subject, message_body, log_id, user='code'):
        """
        Send an HTML E-Mail
        """
        if type(recipients) in [type(''), type(u'')]:
            recipients = [recipients]



        for recipient in recipients:
            try:
                if BadEmail.query.filter(BadEmail.email == recipient).first():
                    return
                self.conn.send_email(self.sender_id, message_subject, message_body, recipient, format='html')

                new_email_sent = EmailSent(self.sender_id, recipient, log_id, datetime.datetime.now())
                db.session.add(new_email_sent)
                db.session.commit()
            except Exception as e:
                err = sys.exc_info()
                print e.message
                raygun.send(err[0], err[1], err[2])
