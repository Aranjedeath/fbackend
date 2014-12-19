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
