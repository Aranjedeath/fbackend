import datetime
from sqlalchemy import Column, Boolean, Float, String, Integer, DateTime, Date, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base


class SearchDefault(Base):
    __tablename__ = 'search_defaults'
    id            = Column(Integer(), primary_key=True)
    category      = Column(String(30))
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    score         = Column(Float(), nullable=False)
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now, nullable=False)


    def __init__(self, user, category, score=0, timestamp=datetime.datetime.now()):
        self.category  = category
        self.user      = user
        self.score     = score
        self.timestamp = timestamp

    def __repr__(self):
        return '<SearchDefault %r:%r:%r>' % (self.categoy, self.user, self.score)