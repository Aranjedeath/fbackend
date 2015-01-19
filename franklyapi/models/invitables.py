from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id
import datetime

class Invitable(Base):
    __tablename__ = 'invitables'
    id = Column(CHAR(32), primary_key=True, default=get_item_id)
    name = Column(String(40), nullable=False)
    twitter_handle = Column(String(40))
    email = Column(String(50))
    profile_picture = Column(String(200))
    gender = Column(Enum('M', 'F'))
    user_title = Column(String(40))
    max_invite_count = Column(Integer(), default=1000)
    twitter_text = Column(String(400))
    mail_text = Column(String(400))
    bio = Column(String(300))
    mail_subject = Column(String(500))

    def __init__(self, name, twitter_handle, email, twitter_text, mail_text, bio, gender, user_title, mail_subject, profile_picture = None, max_invite_count = 1000, id = get_item_id()):
        self.id = id
        self.name = name
        self.twitter_handle = twitter_handle
        self.email = email
        self.profile_picture = profile_picture
        self.gender = gender
        self.user_title = user_title
        self.max_invite_count = max_invite_count
        self.twitter_text = twitter_text
        self.mail_text = mail_text
        self.bio = bio
        self.mail_subject = mail_subject

    def __repr__(self):
        return '<Invitable %r:%r>' % (self.id, self.name)


class Invite(Base):
    __tablename__ = 'user_invites'
    __table_args__ = (UniqueConstraint('user', 'invitable'),)
    id = Column(Integer, primary_key=True)
    user = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    invitable = Column(CHAR(32), ForeignKey('invitables.id'), nullable=False)
    timestamp = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())
    count = Column(Integer(), default=1)

    def __init__(self, user, invitable, count = 1, timestamp = datetime.datetime.now()):
        self.user = user
        self.invitable = invitable
        self.timestamp = timestamp
        self.count = count

    def __repr__(self):
        return '<Invite %r:%r>' % (self.user, self.invitable)
