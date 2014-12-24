import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id
from notification import consider_for_notification

class Event(Base):
    __tablename__     = 'events'
    id                = Column(CHAR(32), primary_key=True, default=get_item_id)
    user              = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    action            = Column(Enum('follow','like','upvote','answer','question','comment'), nullable=False)
    foreign_data      = Column(CHAR(32), nullable=False)
    event_time        = Column(DateTime(), default=datetime.datetime.now)
    for_notification  = Column(Boolean(), default=True)
    notification_sent = Column(Boolean(), default=False)

    def __init__(self, user, action, foreign_data, for_notification=None, notification_sent=False, event_time=datetime.datetime.now(), id=get_item_id()):
        self.id                = id
        self.user              = user
        self.action            = action
        self.foreign_data      = foreign_data
        self.event_time        = event_time 
        self.for_notification  = for_notification or consider_for_notification['action']
        self.notification_sent = notification_sent

    def get_id(self):
        return unicode(self.id)


    def __repr__(self):
        return '<Event %r:%r %r>' % (self.id, self.user, self.action, self.foriegn_data)