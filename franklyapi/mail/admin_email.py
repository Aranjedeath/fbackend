from configs import config
from infra import SimpleMailer

mail_sender = SimpleMailer()
# ADMIN EMAILS
def send_weekly_report(recipients, report):
    mail_sender.send_mail(recipients=recipients, message_subject="Weekly Report", message_body=report, log_id = 'ABCD')


def content_report(recipients, subject, report):
    mail_sender.send_mail(recipients=recipients, message_subject=subject, message_body=report, log_id = 'ABCD')


def cron_job_update(cron_type="Cron heartbeat", message='You only die once - YODO'):
    mail_sender.send_mail(recipients=config.DEV_EMAILS, message_subject=cron_type, message_body= message,
                          log_id = 'ABCD')


def push_stats(body):
    mail_sender.send_mail(recipients=['varun@frankly.me', 'abhishek@frankly.me', 'nikunj@frankly.me'],
                           message_subject='Push Notification Stats', message_body=body, log_id = 'ABCD')