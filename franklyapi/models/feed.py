import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base

class UserFeed(Base):
    __tablename__ = 'user_feeds'
    id            = Column(Integer, primary_key=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False, unique=True)
    day           = Column(String(20), nullable=False)
    score         = Column(Integer(), default=-1, nullable=False)
    changed_at    = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, user, day, score=-1, changed_at=datetime.datetime.now()):
        self.user       = user
        self.day        = day
        self.score      = score
        self.changed_at = changed_at

    def __repr__(self):
        return '<UserFeed %r:%r>' % (self.user, self.day)

class CentralQueueMobile(Base):
    __tablename__ = 'central_queue_mobile'
    id            = Column(Integer, primary_key = True)
    user          = Column(CHAR(32), ForeignKey('users.id'))
    question      = Column(CHAR(32), ForeignKey('questions.id'))
    post          = Column(CHAR(32), ForeignKey('posts.id'))
    day           = Column(Integer, default = 1)
    score         = Column(Integer, default = 0)

    def __init__(self, _type, obj):
        if _type == 'user':
            self.user = obj
        elif _type == 'question':
            self.question = obj
        else:
            self.post = obj

    def __repr__(self):
        if self.user:
            return '<Central Queue: %r -- User: %r >' %(self.id, self.user)
        elif self.question:
            return '<Central Queue: %r -- Question: %r >' %(self.id, self.question)
        else:
            return '<Central Queue: %r -- Post: %r >' %(self.id, self.post)
          
            
        
class IntervalCountMap(Base):
    __tablename__ = 'interval_count_map'
    id            = Column(Integer, primary_key = True)
    minutes       = Column(Integer, default = 0)
    count         = Column(Integer, default = 3)
    
    def __init__(self, minutes, count):
        self.minutes = minutes
        self.count = count

    def __repr__(self):
        return '<Hour Count: %s, %s, %s>'%(self.id, self.minutes, self.count)
