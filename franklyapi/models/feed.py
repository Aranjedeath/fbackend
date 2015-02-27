import datetime
import time
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, CHAR
from database import Base, get_item_id

class DiscoverList(Base):
    __tablename__  = 'discover_list'
    id             = Column(Integer(), primary_key=True)
    post           = Column(CHAR(32), ForeignKey('posts.id'))
    question       = Column(CHAR(32), ForeignKey('questions.id'))
    user           = Column(CHAR(32), ForeignKey('users.id'))
    is_super       = Column(Boolean(), default=False, nullable=False)
    display_on_day = Column(Integer(), nullable=False)
    added_at       = Column(DateTime(), nullable=False)
    #show_order     = Column(Integer())
    removed        = Column(Boolean(), default=False)
    dirty_index    = Column(Integer())

    def __init__(self, post=None, question=None, user=None,
                                    is_super=False, display_on_day=0,
                                    added_at=datetime.datetime.now(),
                                    show_order=None, removed=False, dirty_index=None):            
        if post:
            self.post = post
        elif question:
            self.question = question
        elif user:
            self.user = user
        else:
            raise Exception('Either post or question or user should be provided')
        self.is_super       = is_super
        self.display_on_day = display_on_day 
        self.added_at       = added_at
        self.show_order     = show_order
        self.id             = id
        self.removed        = removed


    def __repr__(self):
        return '<DiscoverList %r:%r>' %(self.id, self.is_super)


class UserFeed(Base):
    __tablename__ = 'user_feeds'
    id            = Column(Integer, primary_key=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False, unique=True)
    day           = Column(String(20), nullable=False)
    score         = Column(Integer(), default=-1, nullable=False)
    changed_at    = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

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

class DateSortedItems(Base):
    __tablename__ = 'date_sorted_items'
    id            = Column(Integer, primary_key = True)
    user          = Column(CHAR(32), ForeignKey('users.id'))
    post          = Column(CHAR(32), ForeignKey('posts.id'))
    score         = Column(Integer, default = 0)
    date          = Column(DateTime, default = datetime.datetime.now())

    def __init__(self, _type, obj_id):
        if _type == 'user':
            self.user = obj_id
        elif _type == 'post':
            self.post = obj_id
        else:
            raise Exception('Type not supported.')
        self.date = datetime.datetime.now()
    
    def __repr__(self):
        if self.user:
            return '<DateSortedItems: %r -- User: %r >' %(self.id, self.user)
        elif self.post:
            return '<DateSortedItems: %r -- Post: %r >' %(self.id, self.post)
