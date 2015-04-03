from configs import config
from apns import APNs, Payload
from models import AccessToken, Notification, UserPushNotification
from notification import helper
from app import db


import gcm
import random
import time
import datetime
import notification_decision

key = helper.key

def push_notification(notification_id, user_id, k=None, source='application'):
    if notification_decision.\
            count_of_push_notifications_sent(user_id=user_id) <= 50: #config.GLOBAL_PUSH_NOTIFICATION_DAY_LIMIT:

        print 'Still under limits for number of daily notifications'
        from controllers import get_item_id
        notification = Notification.query.get(notification_id)

        if k is None:
            k = key[notification.type]

        group_id = '-'.join([str(notification.type), str(notification.object_id)])
        for device in AccessToken.query.filter(AccessToken.user == user_id,
                                               AccessToken.active==True,
                                               AccessToken.push_id!=None).all():


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
                        "icon": notification.icon,
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

                apns = APN()
                apns.send_message([device.push_id], payload)


def get_device_type(device_id):
    if len(device_id) < 17:
        if 'web' in device_id:
            return 'web'
        return 'android'
    return 'ios'


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