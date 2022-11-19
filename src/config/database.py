from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .vars import DB_URL

Base = declarative_base()

engine = create_engine(DB_URL)

Session = sessionmaker()

Base.metadata.bind = engine

Session.configure(bind=engine)

session = Session()
