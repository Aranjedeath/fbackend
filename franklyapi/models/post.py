import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum, CHAR, UniqueConstraint, SmallInteger
from database import Base
from database import get_item_id

class Post(Base):
    __tablename__       = 'posts'
    id                  = Column(CHAR(32), primary_key=True)
    question            = Column(CHAR(32), ForeignKey('questions.id'), nullable=False)
    question_author     = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    answer_author       = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    media_url           = Column(String(300), nullable=False)
    thumbnail_url       = Column(String(300), nullable=False)
    client_id           = Column(String(15), nullable=False, unique=True)
    
    timestamp           = Column(DateTime(), default=datetime.datetime.now())
    answer_type         = Column(Enum('video', 'text', 'picture'), default='video')
    score               = Column(Integer(), default=0)
    deleted             = Column(Boolean(), default=False)
    ready               = Column(Boolean(), default=False)
    popular             = Column(Boolean(), default=False)
    lat                 = Column(Float())
    lon                 = Column(Float())
    location_name       = Column(String(50))
    country_name        = Column(String(50))
    country_code        = Column(String(2))
    view_count          = Column(Integer(), default=0)
    show_after          = Column(SmallInteger(), default = 0)

    added_by            = Column(CHAR(32), ForeignKey('users.id'))
    moderated_by        = Column(CHAR(32), ForeignKey('users.id'))
    ip                  = Column(String(16))
    app_id              = Column(CHAR(32))


    def __init__(self, question, question_author, answer_author, media_url, thumbnail_url, client_id,
                    timestamp=datetime.datetime.now(), answer_type='video', score=0, deleted=False, ready=True,
                    popular=False, lat=None, lon=None, location_name=None, country_name=None, country_code=None,
                    id=None, view_count=0, show_after = 0, added_by=None, moderated_by=None, ip=None, app_id=None):
        self.id              = get_item_id()
        self.question        = question
        self.question_author = question_author
        self.answer_author   = answer_author
        self.media_url       = media_url
        self.thumbnail_url   = thumbnail_url
        self.client_id       = client_id
        
        self.timestamp       = timestamp
        self.answer_type     = answer_type
        self.score           = score
        self.deleted         = deleted
        self.ready           = ready
        self.popular         = popular

        self.lat             = lat
        self.lon             = lon
        self.location_name   = location_name
        self.country_name    = country_name
        self.country_code    = country_code
        self.view_count      = 0
        self.show_after      = show_after

        self.added_by        = added_by
        self.moderated_by    = moderated_by
        
        self.ip              = ip
        self.app_id          = app_id

    def __repr__(self):
        return '<Post %r>' % (self.id)


class PendingPost(Base):
    __tablename__  = 'pending_post'
    __table_args__ = ( UniqueConstraint('user_id', 'question_id'), )
    short_id       = Column(String(15), nullable=False, unique=True, primary_key=True)
    user_id        = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    question_id    = Column(CHAR(32), ForeignKey('questions.id'), nullable=False)
    created_at     = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now)

    def __init__(self, short_id, user_id, question_id, created_at=None):
        self.short_id    = short_id
        self.user_id     = user_id
        self.question_id = question_id
        self.created_at  = created_at or datetime.datetime.now()

    def __repr__(self):
        return '<PendingPost %r:%r>' % (self.user, self.post)

class Like(Base):
    __tablename__  = 'post_likes'
    __table_args__ = ( UniqueConstraint('user', 'post'), )
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    post           = Column(CHAR(32), ForeignKey('posts.id'), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    unliked        = Column(Boolean(), default=False)

    def __init__(self, user, post, unliked=False):
        self.user    = user
        self.post    = post
        self.unliked = unliked

    def __repr__(self):
        return '<Like %r:%r>' % (self.user, self.post)


class PostShare(Base):
    __tablename__  = 'post_shares'
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    post           = Column(CHAR(32), ForeignKey('posts.id'), nullable=False)
    platform       = Column(String(50), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())

    def __init__(self, user, post, platform, timestamp=datetime.datetime.now()):
        self.user      = user
        self.post      = post
        self.platform  = platform
        self.timestamp = timestamp

    def __repr__(self):
        return '<PostShare %r:%r>' % (self.post, self.platform)


class Reshare(Base):
    __tablename__  = 'post_reshares'
    __table_args__ = ( UniqueConstraint('user', 'post'), )
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    post           = Column(CHAR(32), ForeignKey('posts.id'), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now)

    def __init__(self, user, post, timestamp=datetime.datetime.now()):
        self.user      = user
        self.post      = post
        self.timestamp = timestamp
    def __repr__(self):
        return '<Reshare %r:%r>' % (self.user, self.post)


class View(Base):
    __tablename__  = 'post_views'
    __table_args__ = ( UniqueConstraint('user', 'post'), )
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    post           = Column(CHAR(32), ForeignKey('posts.id'), nullable=False)
    first_seen_at  = Column(DateTime(), default=datetime.datetime.now)
    last_seen_at   = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    count          = Column(Integer(), default=1)
    
    def __init__(self, user, post, count=1):
        self.user  = user
        self.post  = post
        self.count = count   

    def __repr__(self):
        return '<View %r:%r>' % (self.user, self.post)
