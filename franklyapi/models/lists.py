from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, CHAR, UniqueConstraint
from database import get_item_id
import datetime

class List(Base):
    __tablename__  = 'lists'
    id             = Column(CHAR(32), primary_key=True)
    name           = Column(String(80), nullable=False)
    display_name   = Column(CHAR(100), nullable=False)
    icon_image     = Column(String(300))
    banner_image   = Column(String(300))
    score          = Column(Float())
    show_on_remote = Column(Boolean(), default=False)
    owner          = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    created_at     = Column(DateTime(), default=datetime.datetime.now())
    created_by     = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    updated_at     = Column(DateTime())
    updated_by     = Column(CHAR(32), ForeignKey('users.id'))
    deleted        = Column(Boolean(), default=False)
    followable     = Column(Boolean(), default=True)

    def __init__(self, name, display_name, created_by, owner=None, show_on_remote=False, 
                        created_at=datetime.datetime.now(), updated_at=None, updated_by=None,
                        score=None, icon_image=None, banner_image=None, followable=False,
                        deleted=False, id=get_item_id()):
        self.name           = name
        self.display_name   = display_name
        self.created_by     = created_by
        self.show_on_remote = show_on_remote
        self.created_at     = created_at
        self.updated_at     = updated_at
        self.updated_by     = updated_by
        self.score          = score
        self.id             = id
        self.followable     = followable
        self.icon_image     = icon_image
        self.banner_image   = banner_image
        self.owner          = owner or created_by
        self.deleted        = deleted

    def __repr__(self):
        return '<List %r:%r:%r>' % (self.id, self.name, self.display_name)


class ListItem(Base):
    __tablename__  = 'list_items'
    id             = Column(Integer(), primary_key=True)
    parent_list_id = Column(CHAR(32), ForeignKey('lists.id'), nullable=False)
    child_user_id  = Column(CHAR(32), ForeignKey('users.id'))
    child_list_id  = Column(CHAR(32), ForeignKey('lists.id'), nullable=False)
    show_on_list   = Column(Boolean(), default=False)
    score          = Column(Float())
    created_at     = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    created_by     = Column(DateTime(), default=datetime.datetime.now())
    is_featured    = Column(Boolean(), default=False)
    deleted        = Column(Boolean(), default=False)

    def __init__(self, parent_list_id, created_by, child_user_id=None, child_list_id=None, 
                show_on_list=False, score=0, created_at=datetime.datetime.now(),
                is_featured=False, deleted=False):
        if not child_user_id:
            self.child_user_id  = child_user_id 
        elif child_list_id:
            self.child_list_id = child_list_id 
        else:
            raise Exception('Either child_list_id or child_user_id must be given')

        self.parent_list_id = parent_list_id
        self.show_on_list   = show_on_list
        self.score          = score
        self.created_at     = created_at
        self.created_by     = created_by
        self.is_featured    = is_featured
        self.deleted        = deleted

    def __repr__(self):
        return '<ListItem %r:%r:%r>' % (self.child_user_id, self.child_list_id, self.parent_list_id)


class ListFollow(Base):
    __tablename__ = 'list_follows'
    __table_args__ = ( UniqueConstraint('user_id', 'list_id'),)
    id            = Column(Integer(), primary_key=True)
    list_id       = Column(CHAR(32), ForeignKey('lists.id'), nullable=False)
    user_id       = Column(CHAR(32), ForeignKey('users.id'), nullable=False)
    unfollowed    = Column(Boolean(), default=False)
    created_at    = Column(DateTime(), default=datetime.datetime.now())

    def __init__(self, list_id, user_id, unfollowed=False, created_at=datetime.datetime.now()):
        self.list_id    = list_id 
        self.user_id    = user_id
        self.created_at = created_at
        self.unfollowed = unfollowed



class Domain(Base):
    __tablename__  = 'domains'
    domain_name    = Column(String(200), primary_key=True)
    list_id        = Column(CHAR(32), ForeignKey('users.id'))
    organisation   = Column(String(80))
    
    def __init__(self, domain_name, list_id=None, organisation=None):
        self.domain_name  = domain_name
        self.list_id      = list_id
        self.organisation = organisation