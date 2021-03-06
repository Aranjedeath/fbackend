import datetime
from sqlalchemy import Column, Boolean, Float, String, Integer, DateTime, Date, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base


class SearchDefault(Base):
    __tablename__ = 'search_defaults'
    id            = Column(Integer(), primary_key=True)
    category      = Column(Integer(), ForeignKey('search_categories.id'), nullable=False)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    score         = Column(Float(), nullable=False)
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now(), nullable=False)
    show_always   = Column(Boolean(), nullable=False, default=False)


    def __init__(self, user, category, score=0, timestamp=datetime.datetime.now(), show_always=False):
        self.category    = category
        self.user        = user
        self.score       = score
        self.timestamp   = timestamp
        self.show_always = show_always

    def __repr__(self):
        return '<SearchDefault %r:%r:%r>' % (self.category, self.user, self.score)


class SearchCategory(Base):
    __tablename__ = 'search_categories'
    id            = Column(Integer(), primary_key=True)
    name          = Column(String(30), nullable=False)
    score         = Column(Float(), nullable=False)
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now(), nullable=False)


    def __init__(self, name, score=0, timestamp=datetime.datetime.now()):
        self.name      = name
        self.score     = score
        self.timestamp = timestamp

    def __repr__(self):
        return '<SearchCategory %r:%r>' % (self.name, self.score)

