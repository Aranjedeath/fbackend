import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, ForeignKey, CHAR, UniqueConstraint
from database import Base


class AdminUser(Base):
    __tablename__        = 'admin_users'
    user_id              = Column(CHAR(32), ForeignKey('users.id'), nullable=False, unique=True)
    
    added_by             = Column(CHAR(32), ForeignKey('users.id'))
    added_on             = Column(DateTime(), default=datetime.datetime.now(), nullable=False)
    
    can_edit_admin       = Column(Boolean(), default=False, nullable=False)
    
    can_add_user         = Column(Boolean(), default=False, nullable=False)
    can_edit_user        = Column(Boolean(), default=False, nullable=False)
    can_delete_user      = Column(Boolean(), default=False, nullable=False)
    
    can_add_post         = Column(Boolean(), default=False, nullable=False)
    can_delete_post      = Column(Boolean(), default=False, nullable=False)
    can_edit_post        = Column(Boolean(), default=False, nullable=False)
    
    can_add_celeb        = Column(Boolean(), default=False, nullable=False)
    can_edit_celeb       = Column(Boolean(), default=False, nullable=False)
    can_delete_celeb     = Column(Boolean(), default=False, nullable=False)
    
    can_add_question     = Column(Boolean(), default=False, nullable=False)
    can_edit_question    = Column(Boolean(), default=False, nullable=False)
    can_delete_question  = Column(Boolean(), default=False, nullable=False)
    
    can_edit_discover    = Column(Boolean(), default=False, nullable=False)
    
    can_view_campus_dash = Column(Boolean(), default=False, nullable=False)
    can_edit_campus_dash = Column(Boolean(), default=False, nullable=False)
    
    deleted              = Column(Boolean(), default=False, nullable=False)





    def __init__(self, user_id, added_by, can_edit_admin=False, can_add_user=False, can_edit_user=False,
                        can_delete_user=False, can_add_celeb=False, can_edit_celeb=False,
                        can_add_post=False, can_edit_post=False, can_delete_post=False,
                        can_delete_celeb=False, can_add_question=False, can_edit_question=False,
                        can_delete_question=False, can_edit_discover=False, can_view_campus_dash=False,
                        can_edit_campus_dash=False, deleted=False, added_on=datetime.datetime.now()):

        self.user_id              = user_id
        self.added_by             = added_by
        self.can_add_user         = can_add_user
        self.can_edit_user        = can_edit_user
        self.can_delete_user      = can_delete_user
        self.can_add_celeb        = can_add_celeb
        self.can_edit_celeb       = can_edit_celeb
        self.can_delete_celeb     = can_delete_celeb
        self.can_add_question     = can_add_question
        self.can_edit_question    = can_edit_question
        self.can_delete_question  = can_delete_question
        self.can_edit_discover    = can_edit_discover
        self.can_add_post         = can_add_post
        self.can_edit_post        = can_edit_post
        self.can_delete_post      = can_delete_post
        self.can_edit_admin       = can_edit_admin
        self.added_on             = added_on
        self.can_view_campus_dash = can_view_campus_dash
        self.can_edit_campus_dash = can_edit_campus_dash
        self.deleted              = deleted
                 
    def __repr__(self):
        return '<AdminUser %r>' % (self.user_id)

