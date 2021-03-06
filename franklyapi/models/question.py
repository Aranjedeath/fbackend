import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, CHAR, UniqueConstraint
from database import Base
from database import get_item_id

class Question(Base):
    __tablename__   = 'questions'
    id              = Column(CHAR(32), primary_key=True)
    question_author = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    question_to     = Column(CHAR(32), ForeignKey('users.id'))
    body            = Column(String(300), nullable=False)
    timestamp       = Column(DateTime(), default=datetime.datetime.now())
    is_answered     = Column(Boolean(), default=False)
    is_anonymous    = Column(Boolean(), default=False)
    is_ignored      = Column(Boolean(), default=False)
    public          = Column(Boolean(), default=False)
    deleted         = Column(Boolean(), default=False)
    added_by        = Column(CHAR(32), ForeignKey('users.id'))
    moderated_by    = Column(CHAR(32), ForeignKey('users.id'))
    short_id        = Column(String(15), unique=True)
    slug            = Column(String(250), nullable=False, unique=True)
    flag            = Column(Integer(), default=1)

    lat             = Column(Float())
    lon             = Column(Float())
    location_name   = Column(String(50))
    country_name    = Column(String(50))
    country_code    = Column(String(2))
    score           = Column(Integer(), default=0)

    ip              = Column(String(16))
    domain_name     = Column(String(200))
    page_url        = Column(String(500))
    app_id          = Column(CHAR(32))
    open_question   = Column(Boolean(), default=False)

    def __init__(self, question_author, question_to, body, short_id, slug, timestamp=datetime.datetime.now(),
                        is_answered=False, is_anonymous=False, is_ignored=False, public=False,
                        deleted=False, moderated_by=None, lat=None, lon=None, location_name=None, 
                        country_name=None, country_code=None, id=None, score=0, added_by=None, flag=1,
                        ip=None, domain_name=None, page_url=None, app_id=None, open_question=False):
        
        self.id              = get_item_id()
        self.question_author = question_author
        self.question_to     = question_to
        self.body            = body
        self.short_id        = short_id
        self.slug            = slug
        self.timestamp       = timestamp
        self.is_answered     = is_answered
        self.is_anonymous    = is_anonymous
        self.is_ignored      = is_ignored
        self.public          = public
        self.deleted         = deleted
        self.moderated_by    = moderated_by
        self.lat             = lat
        self.lon             = lon
        self.location_name   = location_name
        self.country_name    = country_name
        self.country_code    = country_code
        self.score           = score
        self.added_by        = added_by
        self.moderated_by    = moderated_by
        self.flag            = flag

        self.ip              = ip
        self.domain_name     = domain_name
        self.page_url        = page_url
        self.app_id          = app_id
        self.open_question   = open_question

    def __repr__(self):
        return '<Question %r:%r>' % (self.id, self.body)


class Upvote(Base):
    __tablename__  = 'question_upvotes'
    __table_args__ = ( UniqueConstraint('user', 'question'), )
    id             = Column(Integer, primary_key=True)
    user           = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    question       = Column(CHAR(32), ForeignKey('questions.id'), nullable=False)
    timestamp      = Column(DateTime(), onupdate=datetime.datetime.now(), default=datetime.datetime.now())
    downvoted      = Column(Boolean(), default=False)


    def __init__(self, user, question, downvoted=False, timestamp=datetime.datetime.now()):
        self.user      = user
        self.question  = question
        self.downvoted = downvoted
        self.timestamp = timestamp

    def __repr__(self):
        return '<Upvote %r:%r>' % (self.user, self.question)





