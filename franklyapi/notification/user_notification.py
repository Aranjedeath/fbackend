from models import UserNotification
from database import get_item_id
from app import db

import datetime
import push_notification as push

''' Creates relationship between
user and notification
'''


def add_notification_for_user(notification_id, for_users, list_type, push_at=datetime.datetime.now(),k=None):

    for user_id in for_users:
        user_notification = UserNotification(notification_id=notification_id, user_id=user_id,
                                             list_type=list_type, push_at=push_at,
                                             seen_at=None, seen_type=None,
                                             added_at=datetime.datetime.now(),
                                             show_on='all',
                                             id=get_item_id()
                                            )
        db.session.add(user_notification)
        db.session.commit()

        if push_at:
            push.push_notification(notification_id, user_id, k)


