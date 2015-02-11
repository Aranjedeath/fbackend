import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id

class User(Base):
    __tablename__             = 'users'
    id                        = Column(CHAR(32), primary_key=True)
    username                  = Column(String(30), nullable=False, unique=True)
    email                     = Column(String(120), nullable=False, unique=True)
    registered_with           = Column(String(15), nullable=False)
    first_name                = Column(String(250))
    
    facebook_id               = Column(String(120), unique=True)
    twitter_id                = Column(String(120), unique=True)
    google_id                 = Column(String(120), unique=True)
    password                  = Column(String(50))
    
    bio                       = Column(String(200))
    gender                    = Column(Enum('M', 'F'))
    profile_picture           = Column(String(300))
    profile_video             = Column(String(300))

    cover_picture             = Column(String(300))
    facebook_token            = Column(String(400))
    facebook_write_permission = Column(Boolean(), default=False)
    twitter_token             = Column(String(400))
    twitter_secret            = Column(String(400))
    twitter_write_permission  = Column(Boolean(), default=False) 
    google_token              = Column(String(400))
    deleted                   = Column(Boolean(), default=False)
    monkness                  = Column(Integer(), default=-1)
    user_type                 = Column(Integer(), default=0)
    user_title                = Column(String(20))
    phone_num                 = Column(String(20))
    
    lat                       = Column(Float())
    lon                       = Column(Float())
    location_name             = Column(String(50))
    country_name              = Column(String(50))
    country_code              = Column(String(2))    
    user_since                = Column(DateTime(), default=datetime.datetime.now())
    last_updated              = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())   
    last_seen                 = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    allow_anonymous_question  = Column(Boolean(), default=True)
    notify_like               = Column(Boolean(), default=True)
    notify_follow             = Column(Boolean(), default=True)
    notify_question           = Column(Boolean(), default=True)
    notify_comments           = Column(Boolean(), default=True)
    notify_mention            = Column(Boolean(), default=True)
    notify_answer             = Column(Boolean(), default=True)
    timezone                  = Column(Integer(), default=0)
    view_count                = Column(Integer(), default=0)
    total_view_count          = Column(Integer(), default=0)

    def get_user(self,_id):
        self.id = _id
        return self

    def __init__(self, email, username, first_name, registered_with, password=None, facebook_id=None, twitter_id=None, google_id=None,
                        bio=None, gender=None, profile_picture=None, profile_video=None, cover_picture=None,
                        facebook_token=None, facebook_write_permission=False, twitter_token=None,
                        twitter_secret=None, twitter_write_permission=False, google_token=None, deleted=False,
                        monkness=-1, user_type=0, user_title=None, lat=None, lon=None, location_name=None, country_name=None, country_code=None,
                        user_since=datetime.datetime.now(), last_updated=datetime.datetime.now(),
                        last_seen=datetime.datetime.now(), allow_anonymous_question=True,
                        notify_like=True, notify_follow=True, notify_question=True, notify_comments=True,
                        notify_mention=None, notify_answer=None, timezone=0, id=None, phone_num=None, view_count=0, total_view_count=0):
        self.id                        = get_item_id()
        self.email                     = email
        self.first_name                = first_name
        self.username                  = username
        self.registered_with           = registered_with
        self.password                  = password
        self.facebook_id               = facebook_id 
        self.twitter_id                = twitter_id
        self.google_id                 = google_id
        
        self.bio                       = bio                      
        self.gender                    = gender                   
        self.profile_picture           = profile_picture          
        self.profile_video             = profile_video            
        self.cover_picture             = cover_picture            
        self.facebook_token            = facebook_token           
        self.facebook_write_permission = facebook_write_permission
        self.twitter_token             = twitter_token            
        self.twitter_secret            = twitter_secret           
        self.twitter_write_permission  = twitter_write_permission 
        self.google_token              = google_token             
        self.deleted                   = deleted                  
        self.monkness                  = monkness 
        self.user_type                 = user_type
        self.user_title                = user_title

        self.lat                       = lat                      
        self.lon                       = lon                      
        self.location_name             = location_name            
        self.country_name              = country_name             
        self.country_code              = country_code             
        self.user_since                = user_since               
        self.last_updated              = last_updated             
        self.last_seen                 = last_seen                
        self.allow_anonymous_question  = allow_anonymous_question 
        self.notify_like               = notify_like              
        self.notify_follow             = notify_follow            
        self.notify_question           = notify_question          
        self.notify_comments           = notify_comments          
        self.notify_mention            = notify_mention           
        self.notify_answer             = notify_answer            
        self.timezone                  = timezone  
        self.phone_num                 = phone_num 
        self.view_count                = view_count 
        self.total_view_count          = total_view_count             


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


    def __repr__(self):
        return '<User %r:%r>' % (self.id, self.username)



class Follow(Base):
    __tablename__  = 'user_follows'
    __table_args__ = ( UniqueConstraint('user', 'followed'),)
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    followed       = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    unfollowed     = Column(Boolean(), default=False)


    def __init__(self, user, followed, unfollowed=False):
        self.user       = user
        self.followed   = followed
        self.unfollowed = unfollowed

    def __repr__(self):
        return '<Follow %r:%r>' % (self.user, self.followed)


class Block(Base):
    __tablename__  = 'user_blocks'
    __table_args__ = ( UniqueConstraint('user', 'blocked_user'),)
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    blocked_user   = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    unblocked      = Column(Boolean(), default=False)


    def __init__(self, user, blocked_user, unblocked=False):
        self.user         = user
        self.blocked_user = blocked_user
        self.unblocked    = unblocked

    def __repr__(self):
        return '<Block %r:%r>' % (self.user, self.blocked_user)


class UserArchive(Base):
    __tablename__   = 'user_archives'
    id              = Column(Integer, primary_key=True)
    user            = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    username        = Column(String(30), nullable=False)
    first_name      = Column(String(250))
    profile_picture = Column(String(250))
    profile_video   = Column(String(250))
    cover_picture   = Column(String(250))
    bio             = Column(String(200))
    timestamp       = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())


    def __init__(self, user, username, first_name, profile_picture, profile_video, cover_picture, bio):
        self.user            = user
        self.username        = username
        self.first_name      = first_name
        self.profile_picture = profile_picture
        self.profile_video   = profile_video
        self.cover_picture   = cover_picture
        self.bio             = bio

    def __repr__(self):
        return '<UserArchive %r>' % (self.user)


