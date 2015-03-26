import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CHAR

from database import Base



class AccessToken(Base):
    __tablename__ = 'access_tokens'
    access_token  = Column(String(100), nullable=False, primary_key=True)
    device_id     = Column(String(50), nullable=False, unique=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    device_type   = Column(String(10), nullable=False)
    active        = Column(Boolean(), default=True)
    push_id       = Column(String(200))
    last_login    = Column(DateTime(), default=datetime.datetime.now())


    def __init__(self, device_id, user, access_token, device_type, push_id, active=True):
        self.device_id    = device_id
        self.user         = user
        self.access_token = access_token
        self.device_type  = device_type
        self.push_id      = push_id
        self.active       = active        

    def __repr__(self):
        return '<AccessToken %r:%r>' % (self.access_token, self.device_id)


class ForgotPasswordToken(Base):
    __tablename__  = 'forgot_password_tokens'
    token          = Column(String(100), nullable=False, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    email          = Column(String(120), nullable=False)
    created_at     = Column(DateTime(), default=datetime.datetime.now())
    used_at        = Column(DateTime())
    valid          = Column(Boolean(), default=True)

    def __init__(self, token, user, email):
        self.token      = token
        self.user       = user
        self.email      = email
        self.created_at = datetime.datetime.now()
        self.valid      = True


    def __repr__(self):
        return '<ForgotPasswordToken %r:%r>' % (self.user, self.email)
