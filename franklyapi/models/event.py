import datetime
from sqlalchemy import Column, Boolean, DateTime, Date, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id


consider_for_notification = {
                            'follow':True,
                            'like':True,
                            'upvote':True,
                            'answer':True,
                            'question':True,
                            'comment':True
                            }

class Event(Base):
    __tablename__     = 'events'
    __table_args__    = ( UniqueConstraint('user', 'action', 'foreign_data', 'event_date'),)
    id                = Column(CHAR(32), primary_key=True)
    user              = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    action            = Column(Enum('follow','like','upvote','answer','question','comment'), nullable=False)
    foreign_data      = Column(CHAR(32), nullable=False)
    event_time        = Column(DateTime(), default=datetime.datetime.now())
    event_date        = Column(Date(), default=datetime.date.today)
    for_notification  = Column(Boolean(), default=True)
    notification_sent = Column(Boolean(), default=False)

    def __init__(self, user, action, foreign_data, for_notification=None, notification_sent=False, event_time=datetime.datetime.now(), event_date=datetime.date.today, id=get_item_id()):
        self.id                = get_item_id()
        self.user              = user
        self.action            = action
        self.foreign_data      = foreign_data
        self.event_time        = event_time 
        self.for_notification  = for_notification or consider_for_notification[action]
        self.notification_sent = notification_sent
        self.event_date        = event_date

    def get_id(self):
        return unicode(self.id)


    def __repr__(self):
        return '<Event %r:%r %r>' % (self.id, self.user, self.action, self.foriegn_data)
