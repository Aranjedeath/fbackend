from app import dbs


Base = dbs.Model


def get_item_id(id=0):
	import uuid
	return uuid.uuid4().hex

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    db.create_all()
