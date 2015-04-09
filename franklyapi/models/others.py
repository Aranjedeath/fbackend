import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id


class Install(Base):
    __tablename__ = 'installs'
    id            = Column(Integer, primary_key=True)
    device_id     = Column(String(50), nullable=False)
    device_type   = Column(String(20), nullable=False)
    url           = Column(String(250))
    ref_data      = Column(String(250))
    uninstalled   = Column(Boolean(), default=False)
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

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
    video_type    = Column(String(20))
    object_id     = Column(CHAR(32))
    task_id       = Column(CHAR(32))
    username      = Column(String(30))
    thumbnail     = Column(String(300), nullable=False)
    opt           = Column(String(300)) # 700
    medium        = Column(String(300)) # 300
    low           = Column(String(300)) # 150
    ultralow      = Column(String(300)) # 45
    promo         = Column(String(300)) # promo
    delete        = Column(Boolean(), default=False)
    process_state = Column(Enum('pending', 'running', 'success', 'failed'), default='pending')
    created_at    = Column(DateTime(), default=datetime.datetime.now())

    def __init__(self, url, video_type, object_id, username=None, thumbnail=None, opt=None, medium=None, low=None, ultra_low=None,
                        process_state='pending' ,delete=False,
                        created_at=datetime.datetime.now()):
        self.url           = url
        self.video_type    = video_type
        self.object_id     = object_id
        self.thumbnail     = thumbnail
        self.username      = username
        self.opt           = opt
        self.medium        = medium
        self.low           = low
        self.ultra_low     = ultra_low
        self.delete        = delete
        self.process_state = process_state
        self.created_at    = created_at

    def __repr__(self):
        return '<Video %r:%r>' % (self.process_state, self.url)


class DashVideo(Base):
    __tablename__             = 'dash_videos'
    url                       = Column(CHAR(300), ForeignKey('videos.url'), nullable = False)
    dash_url                  = Column(CHAR(300), primary_key=True)

    def __init__(self, base_url, dash_url):
        self.url = base_url
        self.dash_url = dash_url
        
    def __repr__(self):
        return '<DashVideo %r:%r>' % (self.url, self.dash_url)

class EncodeLog(Base):
    __tablename__ = 'encode_log'
    id              = Column(Integer, primary_key=True)
    video_url       = Column(String(300))
    video_quality   = Column(String(20))
    start_time      = Column(DateTime(), default=datetime.datetime.now())
    finish_time     = Column(DateTime(), default=None, nullable=True)
    success         = Column(Boolean, default=False)
    def __init__(self,video_url,video_quality='',start_time=datetime.datetime.now(),finish_time=None,success=None):
        self.video_url      = video_url
        self.video_quality  = video_quality
        self.start_time     = start_time
        self.finish_time    = finish_time
        self.success        = success

    def __repr__(self):
        return '<EventLog %r:%r>' % (self.start_time,self.finish_time)


class ReportAbuse(Base):
    __tablename__ = 'report_abuse'
    id            = Column(Integer, primary_key=True)
    user_by       = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    entity_type   = Column(Enum('post', 'user', 'question', 'comment'), nullable=False)
    entity_id     = Column(CHAR(32), nullable=False)
    reason        = Column(String(300))
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

    def __init__(self, user_by, entity_type, entity_id, reason=None):
        self.user_by        = user_by
        self.entity_type = entity_type
        self.entity_id   = entity_id
        self.reason      = reason
        self.timestamp   = datetime.datetime.now()

    def __repr__(self):
        return '<ReportAbuse %r:%r>' % (self.entity_type, self.entity_id)


class Feedback(Base):
    __tablename__ = 'feedbacks'
    id            = Column(Integer, primary_key=True)
    user          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    medium        = Column(String(50))
    message       = Column(String(300))
    email         = Column(String(120))
    version       = Column(String(10))
    timestamp     = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

    def _medium_is_valid(self, medium):
        medium_components = medium.split('-')
        if not medium_components[0] in ['android', 'ios', 'web']:
            return False
        if len(medium_components) != 2:
            return False
        return True

    def __init__(self, user, medium, message=None, email=None, version=None, timestamp=datetime.datetime.now()):
        medium = medium.lower()
        if not self._medium_is_valid(medium):
            raise Exception('medium should be of format <platform_type>-<screen>')
        self.user    = user
        self.medium  = medium
        self.message = message
        self.email   = email
        self.version = version
        self.timestamp = timestamp

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
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

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
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

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
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
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
    timestamp        = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

    def __init__(self, device_id, account_pname, account_username, user=None):
        self.device_id        = device_id
        self.account_pname    = account_pname
        self.account_username = account_username
        self.user             = user

    def __repr__(self):
        return '<UserAccount %r:%r>' % (self.account_pname, self.account_username)

class ContactUs(Base):
    __tablename__ = 'contact_us'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable = False)
    email = Column(String(60), nullable = False)
    message = Column(String(400), nullable = False)
    organisation = Column(String(40), nullable = False)
    phone = Column(String(20), nullable = False)
    b64msg = Column(String(450), nullable = False)

    def __init__(self,name, email, organisation, message, phone, b64msg):
        self.name = name
        self.email = email
        self.message = message
        self.organisation = organisation
        self.phone = phone
        self.b64msg = b64msg


class Stats(Base):
    __tablename__ = 'stats'
    id = Column(Integer, primary_key=True)
    total_video_view_count = Column(Integer, nullable=False)
    counted_on = Column(DateTime())

    def __init__(self,total_video_view_count,counted_on):
        self.total_video_view_count = total_video_view_count
        self.counted_on = counted_on

class Tester(Base):
    __tablename__ = 'testers'
    id            = Column(CHAR(32), primary_key=True)
    username      = Column(String(100), nullable=False)
    

    def __init__(self,username):
        self.id           = get_item_id()
        self.username     = username

    def __repr__(self):
        return '<Tester %r:%r>' % (self.id, self.username)

class ProfileRequest(Base):
    __tablename__ = 'profile_requests'
    id = Column(CHAR(32), primary_key=True)
    request_for = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    request_by = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    request_type = Column(String(45), nullable=False)
    request_count = Column(Integer, default = 1)
    created_at = Column(DateTime(), default=datetime.datetime.now())
    updated_at = Column(DateTime())

    def __init__ (self):
        self.id = get_item_id()

    def __repr__(self):
        return '<ProfileRequests %r:%r>' %(self.request_by, self.request_for)


class MailLog(Base):
    __tablename__ = 'mail_log'

    id= Column(CHAR(32), primary_key=True)
    email_id = Column(CHAR(100))
    mail_type = Column(CHAR(45))
    object_id = Column(CHAR(100))
    created_at = Column(DateTime(), default=datetime.datetime.now())
    updated_at = Column(DateTime(), default=datetime.datetime.now())

    def __init__ (self, email_id, mail_type, object_id):
        self.id = get_item_id()
        self.email_id = email_id
        self.mail_type = mail_type
        self.object_id = object_id

    def __repr__(self):
        return '<MailLog %r:%r>' %(self.id, self.email_id, self.mail_type, self.object_id, self.created_at)
    