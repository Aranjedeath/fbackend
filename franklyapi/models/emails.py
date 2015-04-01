import datetime
from app import db
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CHAR
from database import Base

from database import get_item_id

class Email(Base):
    __tablename__ = 'emails'
    id            = Column(CHAR(32), primary_key=True)
    created_by    = Column(CHAR(32), nullable=False)
    from_e        = Column(String(100), nullable=False)
    subject       = Column(String(200), nullable=False)
    body          = Column(String(10000), nullable=False)
    created_at    = Column(DateTime(), default=datetime.datetime.now())


    def __init__(self,created_by, from_e, subject, body, created_at=datetime.datetime.now()):
        self.id           = get_item_id()
        self.created_by   = created_by
        self.from_e       = from_e
        self.subject      = subject
        self.body         = body
        self.created_at   = created_at   

    def __repr__(self):
        return '<Email %r:%r:%r>' % (self.id, self.from_e, self.to)

class EmailSent(Base):
    __tablename__ = 'email_sent'
    id            = Column(CHAR(32), primary_key=True)
    from_e        = Column(String(100), nullable=False)
    to            = Column(String(100), nullable=False)
    email_id      = Column(CHAR(32), nullable=False)
    sent_at       = Column(DateTime(), default=datetime.datetime.now())


    def __init__(self, from_e, to, email_id, sent_at=datetime.datetime.now()):
        self.id           = get_item_id()
        self.from_e       = from_e
        self.to           = to
        self.email_id     = email_id
        self.sent_at      = sent_at       

    def __repr__(self):
        return '<EmailSent %r:%r:%r:%r>' % (self.id, self.from_e, self.to, self.email_id)

class BadEmail(Base):
    __tablename__  = 'bad_emails'
    id             = Column(CHAR(32), primary_key=True)
    email          = Column(String(100), nullable=False, unique=True)
    reason_type    = Column(String(100), nullable=False)
    reason_subtype = Column(String(100), nullable=False)
    timestamp      = Column(DateTime(), default=datetime.datetime.now())

    def __init__(self, email, reason_type, reason_subtype, timestamp=datetime.datetime.now()):
        self.id             = get_item_id()
        self.email          = email
        self.reason_type    = reason_type
        self.reason_subtype = reason_subtype
        self.timestamp      = timestamp

    def __repr__(self):
        return '<BadEmail %r:%r>' % (self.email, self.reason_type)