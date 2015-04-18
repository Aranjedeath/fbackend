import random
import time
import datetime
import gcm
import util

from apns import APNs, Payload
from sqlalchemy.sql import text
from models import Notification, UserPushNotification
from app import db
from configs import config
from database import get_item_id
from notification.commons import helper



key = helper.key


def send(notification_id, user_id, k=None, source='application', notification_limit=config.GLOBAL_PUSH_NOTIFICATION_DAY_LIMIT):

    devices = util.get_active_mobile_devices(user_id)

    should_push = util.count_of_push_notifications_sent(user_id=user_id) \
                                       <= notification_limit

    notification = Notification.query.get(notification_id)



    ''' Only if the user has valid devices to be pushed to and is
    under global limit for the same'''

    if len(devices) and should_push:
        print 'Still under limits for number of daily notifications'
        k = key[notification.type] if k is None else k

        group_id = '-'.join([str(notification.type), str(notification.object_id)])

        for device in devices:
            print 'Found valid devices for push notifications'


            user_push_notification = UserPushNotification(notification_id=notification_id,
                                                               user_id=user_id,
                                                              device_id=device.device_id,
                                                              push_id=device.push_id,
                                                              added_at=datetime.datetime.now(),
                                                              pushed_at=datetime.datetime.now(),
                                                              clicked_at=None,
                                                              source=source,
                                                              cancelled=False,
                                                              result=None,
                                                              id=get_item_id())
            db.session.add(user_push_notification)
            db.session.commit()
            payload = {
                             "user_to": user_id,
                             "type": 1,
                             "id": user_push_notification.id,
                             "notification_id": notification.id,
                             "heading": k['title'],
                             "text": notification.text.replace('<b>', '').replace('</b>', ''),
                             "styled_text": notification.text,
                             "icon_url": notification.icon,
                             "cover_image": None,
                             "group_id": group_id,
                             "link": notification.link,
                             "deeplink": notification.link,
                             "timestamp": int(time.mktime(user_push_notification.added_at.timetuple())),
                             "seen": False,
                             "label_one": k['label_one'],
                             "label_two": k['label_two']
                         }

            if get_device_type(device.device_id) == 'android':
                print 'pushing gcm for android'
                gcm_sender = GCM()
                gcm_sender.send_message([device.push_id], payload)

            if get_device_type(device.device_id) == 'ios':
                print 'pushing for iOS'
                print 'For Push id', device.push_id
                apns = APN()
                payload = get_payload_apns(payload=payload)
                print payload
                apns.send_message([device.push_id], payload)




def get_device_type(device_id):
    if len(device_id) < 17:
        if 'web' in device_id:
            return 'web'
        return 'android'
    return 'ios'

def get_payload_apns(payload):

    return {
             "aps": {
                        "alert":  payload['text'],
                        "badge": 1,
                        "sound": "default"
                   },

                "group_id": payload['group_id'],
                "id": payload['id'],
                "link": payload["deeplink"],
                "seen": payload['seen'],
                "timestamp":payload['timestamp'],
                "user_to":payload['user_to']

           }


def stats():

    results = db.session.execute(text('''SELECT count(*), user_id FROM user_notifications
                                         WHERE added_at > date_sub(now(), interval 1 day)
                                         GROUP BY user_id ; '''))
    total_in_app_notifications = 0
    pushable_devices = 0
    for row in results:
        total_in_app_notifications += row[0]
        devices = helper.get_active_mobile_devices(row[1])
        pushable_devices += 0 if devices is None else len(devices)

    body = 'Total in app notifications created: ' + str(total_in_app_notifications)

    body += '<br/><br/> Number of active devices available for these notifications: %s' % str(pushable_devices)

    results = db.session.execute(text('''Select count(*) from user_push_notifications
                                         where pushed_at > date_sub(now(), interval 1 day)'''))

    for row in results:
        total_push_notifications = row[0]

    body += '<br/><br/> Total Push Notifications sent: ' + str(total_push_notifications)

    results = db.session.execute(text('''Select count(*) from user_push_notifications
                                         where pushed_at > date_sub(now(), interval 1 day)
                                         group by user_id ;'''))
    unique_users = 0
    users_at_limit = 0
    for user in results:
        unique_users += 1
        if user[0] >= config.GLOBAL_PUSH_NOTIFICATION_DAY_LIMIT:
            users_at_limit += 1

    body += '<br/><br/> Unique Users: ' + str(unique_users)
    body += '<br/><br/> Users who have received %s notifications: %s' \
             % (config.GLOBAL_PUSH_NOTIFICATION_DAY_LIMIT, users_at_limit)




    results = db.session.execute(text('''Select n.type, count(n.id)
                                         from user_notifications un
                                         left join notifications n on n.id = un.notification_id
                                         where un.added_at > date_sub(now(), interval 1 day)
                                         group by n.type ;
                                      '''))

    body += '<br/><br/><br/> In app notification distribution: <table border=1 width=100%> <tbody> '

    for type in results:
        body += '<tr><td width="50%">' + str(type[0]) + '</td><td width="20%">' + str(type[1]) + '</td></tr>'

    body += '</tbody></table>'

    results = db.session.execute(text('''Select n.type, count(n.id)
                                         from user_push_notifications upn
                                         left join notifications n on n.id = upn.notification_id
                                         where upn.pushed_at > date_sub(now(), interval 1 day)
                                         group by n.type ;
                                      '''))

    body += '<br/><br/><br/> Push notification distribution: <table border=1 width=100%> <tbody> '

    for type in results:
        body += '<tr><td width="50%">' + str(type[0]) + '</td><td width="20%">' + str(type[1]) + '</td></tr>'

    body += '</tbody></table>'

    from franklyapi.mail import admin_email
    admin_email.push_stats(body)


class GCM():

    def __init__(self, api_key=config.GCM_API_KEY):
        self.gcm = gcm.GCM(api_key)

    def send_message(self, gcm_ids, data):
        self.gcm.json_request(registration_ids=gcm_ids, data=data)


class APN():

    def __init__(self, cert_file=config.APN_CERT_PATH, key_file=config.APN_KEY_PATH, use_sandbox=False):
        self.apns = APNs(use_sandbox=True, cert_file=cert_file, key_file=key_file, enhanced=True)



    def send_message(self, apn_ids, data):

        def response_listener(error_response):
            print error_response

        payload = Payload(custom=data)
        identifier = random.getrandbits(32)
        self.apns.gateway_server.register_response_listener(response_listener)

        for id in apn_ids:
            self.apns.gateway_server.send_notification(id, payload, identifier=identifier)