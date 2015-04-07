from configs import config
from infra import SimpleMailer


# ADMIN EMAILS
def send_weekly_report(recipients, report):
    mail_sender.send_mail(recipients, "Weekly Report", report)


def content_report(recipients, subject, report):
    mail_sender.send_mail(recipients, subject, report)


def cron_job_update(cron_type="Cron heartbeat", message='You only die once - YODO'):
    mail_sender.send_mail(config.DEV_EMAILS, cron_type, message)


def push_stats(body):
    mail_sender.send_mail(['varun@frankly.me','abhishek@frankly.me','nikunj@frankly.me'],
                           'Push Notification Stats', body)