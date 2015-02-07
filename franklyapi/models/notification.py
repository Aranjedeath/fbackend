import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base, get_item_id


class Notification(Base):
    __tablename__ = 'notifications'
    id            = Column(CHAR(32), primary_key=True, default=get_item_id())
    type          = Column(String(30), nullable=False)
    link          = Column(String(200), nullable=False)
    object_id     = Column(CHAR(32), nullable=False)
    icon          = Column(String(100), nullable=False)
    created_at    = Column(DateTime(), default=datetime.datetime.now())
    manual        = Column(Boolean(), default=False)

    def _type_is_valid(self, type):
        type_components = type.split('-')
        if len(type_components) != 2:
            return False
        return True

    def _icon_is_valid(self, icon):
        icon_components = icon.split('-')
        if len(icon_components) != 4:
            return False
        if icon_components[0] == 'url' and not icon_components[3].startswith('http'):
            return False
        return True


    def __init__(self, type, link, object_id, icon, created_at=datetime.datetime.now(), manual=False, id=get_item_id()):
        if not self._type_is_valid(type):
            raise Exception('type should be of format <object>-<action>')
        if not self._icon_is_valid(type):
            raise Exception('icon should be of format <icon_type>-<object>-<property>-<object_id>')

        self.id         = id
        self.type       = type
        self.link       = link
        self.object_id  = object_id
        self.icon       = icon,
        self.created_at = created_at
        self.manual     = manual


    def __repr__(self):
        return '<Notification %r:%r>' % (self.type, self.id)


class UserNotification(Base):
    __tablename__   = 'user_notifications'
    id              = Column(CHAR(32), primary_key=True, default=get_item_id())
    notification_id = Column(CHAR(32), ForeignKey('notifications.id'), nullable=False)
    user_id         = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    push_at         = Column(DateTime(), default=datetime.datetime.now())
    seen_at         = Column(DateTime())
    seen_type       = Column(String(10))
    list_type       = Column(String(10), default='me')
    added_at        = Column(DateTime(), default=datetime.datetime.now())


    def __init__(self, notification_id, user_id, list_type, push_at=datetime.datetime.now(),
                        seen_at=None, seen_type=None,
                        added_at=datetime.datetime.now(), id=get_item_id()):
        self.id              = id
        self.notification_id = notification_id
        self.user_id         = user_id
        self.push_at         = push_at
        self.seen_at         = seen_at
        self.seen_type       = seen_type
        self.added_at        = added_at


    def __repr__(self):
        return '<UserNotification %r:%r>' % (self.user_id, self.notification_id)


class UserPushNotification(Base):
    __tablename__   = 'user_push_notifications'
    id              = Column(CHAR(32), primary_key=True, default=get_item_id())
    notification_id = Column(CHAR(32), ForeignKey('notifications.id'), nullable=False)
    user_id         = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    device_id       = Column(String(50), nullable=False)
    push_id         = Column(String(200), nullable=False)
    added_at        = Column(DateTime(), default=datetime.datetime.now())
    pushed_at       = Column(DateTime())
    clicked_at      = Column(String(10))
    source          = Column(String(10), default='application')
    cancelled       = Column(Boolean(), default=False)


    def __init__(self, notification_id, user_id, device_id, push_id,
                        added_at=datetime.datetime.now(), pushed_at=None, clicked_at=None,
                        source='application', cancelled=False, id=get_item_id()):
        self.id              = id
        self.notification_id = notification_id
        self.user_id         = user_id
        self.device_id       = device_id
        self.push_id         = push_id
        self.added_at        = added_at
        self.pushed_at       = pushed_at
        self.clicked_at      = clicked_at
        self.source          = source
        self.cancelled       = cancelled


    def __repr__(self):
        return '<UserPushNotification %r:%r:%r>' % (self.notification_id, self.device_id, self.pushed_at)
