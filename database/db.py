from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from database.models import Base

sqlite_url = "sqlite:///coworking.db"
sqlite_engine = create_engine(sqlite_url)
Session = sessionmaker(bind=sqlite_engine)
sqlite_session = Session()

Base.metadata.create_all(sqlite_engine)

