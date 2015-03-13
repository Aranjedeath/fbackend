import mailconfig
import boto.ses

class SimpleMailer:
    """
    Class defining the simple mailer
    """
    def __init__(self,sender, key=mailconfig.aws_access_key_id,secret_key=mailconfig.aws_secret_access_key, region='us-east-1'):
        """
        Initializes the SES connection and sets up the sender mail ID
        """
        self.sender_id = sender
        self.conn = boto.ses.connect_to_region(region,aws_access_key_id=key, aws_secret_access_key=secret_key)

    def send_to(self,reciever_id, message_subject, message_body):
        """
        Send an HTML E-Mail
        """
        self.conn.send_email(self.sender_id, message_subject, message_body, [reciever_id], format='html')


if __name__ == '__main__':
    me = SimpleMailer('nikhil@frankly.me')
    me.send_to('hellking4u@gmail.com','Test Mail','<b>Is</b><h1>good</h1>')