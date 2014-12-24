import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id

class Event(Base):
    __tablename__             = 'events'
    id                        = Column(CHAR(32), primary_key=True, default=get_item_id)
    user                      = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    action                    = Column(mysql.ENUM('follow','like','upvote','answer','question','comment'), nullable=False)
    foriegn_data              = Column(CHAR(32), nullable=False)
    event_time                = Column(DateTime(), default=datetime.datetime.now)
    for_notification          = Column(Boolean(), default=True)
    notification_sent         = Column(Boolean(), default=False)

    def __init__(self, user, action, foriegn_data, even_time=datetime.datetime.now(), for_notification=True, notification_sent=True):
        self.id                        = id
        self.user                      = user
        self.action                    = action
        self.foriegn_data              = foriegn_data
        self.event_time                = event_time 
        self.for_notification          = for_notification
        self.notification_sent         = notification_sent

    def get_id(self):
        return unicode(self.id)


    def __repr__(self):
        return '<Event %r:%r %r>' % (self.id, self.user, self.action, self.foriegn_data)