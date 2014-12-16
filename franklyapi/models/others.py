import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base


class Install(Base):
    __tablename__ = 'installs'
    id            = Column(Integer, primary_key=True)
    device_id     = Column(String(50), nullable=False)
    device_type   = Column(String(20), nullable=False)
    url           = Column(String(250))
    ref_data      = Column(String(250))
    uninstalled   = Column(Boolean(), default=False)
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, device_id, device_type, url=None, ref_data=None, uninstalled=False):
        self.device_id   = device_id
        self.device_type = device_type
        self.url         = url
        self.ref_data    = ref_data
        self.uninstalled = uninstalled

    def __repr__(self):
        return '<Install %r:%r>' % (self.device_id, self.uninstalled)


class Video(Base):
    __tablename__ = 'videos'
    url           = Column(String(300), primary_key=True)
    thumbnail     = Column(String(300))
    opt           = Column(String(300)) # 700
    medium        = Column(String(300)) # 300
    low           = Column(String(300)) # 150
    ultralow     = Column(String(300)) # 45
    promo         = Column(String(300)) # promo
    delete        = Column(Boolean(), default=False)
    process_state = Column(Enum('pending', 'running', 'success', 'failed'), default='pending')
    created_at    = Column(DateTime(), default=datetime.datetime.now)

    def __init__(self, url, thumbnail=None, opt=None, medium=None, low=None, ultra_low=None, 
                        process_state='pending' ,delete=False, 
                        created_at=datetime.datetime.now()):
        self.url           = url
        self.opt           = opt 
        self.medium        = medium 
        self.low           = low 
        self.ultra_low     = ultra_low 
        self.delete        = delete
        self.process_state = process_state
        self.created_at    = created_at

    def __repr__(self):
        return '<Video %r:%r>' % (self.process_state, self.url)


class ReportAbuse(Base):
    __tablename__ = 'report_abuse'
    id            = Column(Integer, primary_key=True)
    user_by       = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    entity_type   = Column(Enum('post', 'user', 'question', 'comment'), nullable=False)
    entity_id     = Column(CHAR(32), nullable=False)
    reason        = Column(String(300))
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, user, entity_type, entity_id, reason=None):
        self.user        = user
        self.entity_type = entity_type
        self.entity_id   = entity_id
        self.reason      = reason

    def __repr__(self):
        return '<ReportAbuse %r:%r>' % (self.entity_type, self.entity_id)


class Email(Base):
    __tablename__ = 'emails'
    id            = Column(Integer, primary_key=True)
    email         = Column(String(120), nullable=False, unique=True)
    email_status  = Column(Enum("invalid","bounce","complaint","unsubscribe"), nullable=False)
    message       = Column(String(200))
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, email, email_status, message=None):
        self.email        = email
        self.email_status = email_status
        self.message      = message

    def __repr__(self):
        return '<Email %r:%r>' % (self.email, self.email_status)

class Feedback(Base):
    __tablename__ = 'feedbacks'
    id            = Column(Integer, primary_key=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    medium        = Column(String(50))
    message       = Column(String(300))
    email         = Column(String(120))
    version       = Column(String(10))
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, user, medium, message=None, email=None, version=None):
        self.user    = user
        self.medium  = medium
        self.message = message
        self.email   = email
        self.version = version

    def __repr__(self):
        return '<Feedback %r:%r>' % (self.user, self.medium)


class Interest(Base):
    __tablename__  = 'user_interests'
    __table_args__ = ( UniqueConstraint('user', 'interest', 'source'),)
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    interest       = Column(String(200), nullable=False)
    score          = Column(Float(), default=0)
    source         = Column(String(20))
    category       = Column(String(20))
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, user, interest, score=0, source=None, category=None):
        self.user     = user
        self.interest = interest
        self.score    = score
        self.source   = source
        self.category = category

    def __repr__(self):
        return '<Interest %r:%r>' % (self.interest, self.user)


class UserData(Base):
    __tablename__ = 'user_data'
    id            = Column(Integer, primary_key=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    name          = Column(String(250))
    email         = Column(String(120))
    hometown      = Column(String(100))
    birthday      = Column(DateTime())
    work          = Column(String(250))
    education     = Column(String(250))
    current_city  = Column(String(100))
    gender        = Column(Enum('M', 'F'))

    def __init__(self, user, name=None, email=None, hometown=None, birthday=None, work=None, education=None, current_city=None, gender=None):
        self.user         = user
        self.name         = name
        self.email        = email
        self.hometown     = hometown
        self.birthday     = birthday
        self.work         = work
        self.education    = education
        self.current_city = current_city
        self.gender       = gender

    def __repr__(self):
        return '<UserData %r>' % (self.user)
    

class Contact(Base):
    __tablename__  = 'user_contacts'
    __table_args__ = ( UniqueConstraint('user', 'contact', 'contact_type'),)
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'))
    contact        = Column(String(120), nullable=False)
    contact_type   = Column(String(20), nullable=False)
    contact_name   = Column(String(120))
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, contact, contact_type, contact_name=None, user=None):
        self.user         = user
        self.contact      = contact
        self.contact_type = contact_type
        self.contact_name = contact_name

    def __repr__(self):
        return '<Contact %r:%r>' % (self.contact_type, self.contact)


class Package(Base):
    __tablename__  = 'device_packages'
    __table_args__ = ( UniqueConstraint('user', 'device_id','package_name'),)
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'))
    device_id      = Column(String(50), nullable=False)
    package_name   = Column(String(100), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())
    platform_type  = Column(String(20), default='android')

    def __init__(self, device_id, package_name, user=None, platform_type='android'):
        self.device_id    = device_id
        self.package_name = package_name
        self.user         = user
        self.platform     = platform_type

    def __repr__(self):
        return '<Package %r:%r>' % (self.package, self.device_id)

class UserAccount(Base):
    __tablename__    = 'user_accounts'
    __table_args__   = ( UniqueConstraint('user', 'device_id','account_pname'),)
    id               = Column(Integer, primary_key=True)
    user             = Column(CHAR(32), ForeignKey('users.id'))
    device_id        = Column(String(50), nullable=False)
    account_pname    = Column(String(100), nullable=False)
    account_username = Column(String(50), nullable=False)
    timestamp        = Column(DateTime(), onupdate=datetime.datetime.now, default=datetime.datetime.now())

    def __init__(self, device_id, account_pname, account_username, user=None):
        self.device_id        = device_id
        self.account_pname    = account_pname
        self.account_username = account_username
        self.user             = user

    def __repr__(self):
        return '<UserAccount %r:%r>' % (self.account_pname, self.account_username)


