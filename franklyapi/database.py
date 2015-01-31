from app import db


Base = db.Model


def get_item_id(id=0):
    import uuid
    from random import choice
    chars = ['a','b','c','d','e','0','1','2','3','4','5','6','7','8','9']
    arr = [choice(chars) for i in range(32)]
    _id = ''.join(arr)
    print "I generated id", _id
    return _id
#return uuid.uuid4().hex

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    db.create_all()
