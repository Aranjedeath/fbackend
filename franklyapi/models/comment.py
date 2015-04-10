import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, CHAR
from database import Base

from database import get_item_id

class Comment(Base):
    __tablename__  = 'comments'
    id             = Column(CHAR(32), primary_key=True)
    on_post        = Column(CHAR(32), ForeignKey('posts.id'), nullable=False)
    comment_author = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    body           = Column(String(300), nullable=False)
    timestamp      = Column(DateTime(), default=datetime.datetime.now())
    deleted        = Column(Boolean(), default=False)
    
    lat            = Column(Float())
    lon            = Column(Float())
    location_name  = Column(String(50))
    country_name   = Column(String(50))
    country_code   = Column(String(2))

    ip              = Column(String(16))
    domain_name     = Column(String(200))
    page_url        = Column(String(500))
    app_id          = Column(CHAR(32))


    def __init__(self, on_post, comment_author, body, timestamp=datetime.datetime.now(), deleted=False,
                    lat=None, lon=None, location_name=None, country_name=None, country_code=None, id=None,
                    ip=None, domain_name=None, page_url=None, app_id=None):
        self.id             = get_item_id()
        self.on_post        = on_post
        self.comment_author = comment_author
        self.body           = body
        self.timestamp      = timestamp
        self.deleted        = deleted
        
        self.lat            = lat            
        self.lon            = lon            
        self.location_name  = location_name  
        self.country_name   = country_name   
        self.country_code   = country_code 
        self.ip             = ip
        self.domain_name    = domain_name
        self.page_url       = page_url
        self.app_id         = app_id  

    def __repr__(self):
        return '<Comment %r:%r>' % (self.id, self.on_post)
