from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from configs import config
#from flask.ext.script import Manager
#from flask.ext.migrate import Migrate, MigrateCommand

engine = create_engine(config.DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=False,
                                         bind=engine))




Base = declarative_base()
Base.query = db_session.query_property()

def get_item_id(id=0):
	import uuid
	return uuid.uuid4().hex

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

'''
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
'''
