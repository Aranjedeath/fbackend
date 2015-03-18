import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, CHAR, Enum
from database import Base

class InflatedStat(Base):
    __tablename__  = 'inflated_stats'
    id             = Column(Integer(), primary_key=True)
    object_type    = Column(Enum('user', 'post', 'question'), nullable=False)
    post           = Column(CHAR(32), ForeignKey('posts.id'), unique=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), unique=True)
    question       = Column(CHAR(32), ForeignKey('questions.id'), unique=True)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), nullable=False)
    view_count     = Column(Integer(), nullable=False, default=0)
    like_count     = Column(Integer(), nullable=False, default=0)
    follower_count = Column(Integer(), nullable=False, default=0)
    upvote_count   = Column(Integer(), nullable=False, default=0)


    def __init__(self, post=None, user=None, question=None, view_count=0, like_count=0, follower_count=0, upvote_count=0, timestamp=datetime.datetime.now()):
        if user:
            self.object_type    = 'user'
            self.user           = user
            self.follower_count = follower_count

        elif post:
            self.object_type = 'post'
            self.post        = post
            self.like_count  = like_count

        elif question:
            self.object_type  = 'question'
            self.question     = question
            self.upvote_count = upvote_count

        else:
            raise Exception('Either post or user or question must be provided')

        self.view_count = view_count
        self.timestamp  = timestamp

    

    def __repr__(self):
        object_id = self.user or self.post
        return '<InflatedStat %r:%r>' % (self.object_type, object_id)

