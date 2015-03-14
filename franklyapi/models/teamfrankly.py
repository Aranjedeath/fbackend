import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, UniqueConstraint

from database import Base


class TeamFrankly(Base):
    __tablename__  = 'team_frankly'
    __table_args__    = ( UniqueConstraint('token_type', 'external_id'))
    id             = Column(Integer(), primary_key=True)
    external_id    = Column(String(300), nullable=False)
    name           = Column(String(300), nullable=False)
    token_type     = Column(Enum('facebook', 'twitter', 'google'), nullable=False)
    token          = Column(String(300), nullable=False)
    token_secret   = Column(String(300), nullable=False)
    email          = Column(String(300), nullable=False)
    added_at       = Column(DateTime(), nullable=False)


    def __init__(self, external_id, name, token_type, token, token_secret, email, added_at=datetime.datetime.now()):            
        self.id           = id
        self.external_id  = external_id
        self.name         = name
        self.token_type   = token_type
        self.token        = token
        self.token_secret = token_secret
        self.email        = email
        self.added_at     = added_at           

    def __repr__(self):
        return '<TeamFrankly %r:%r>' %(self.token_type, self.name)
