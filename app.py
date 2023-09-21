from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sqlite_url = "sqlite:///mydatabase.db"
sqlite_engine = create_engine(sqlite_url)
Session = sessionmaker()
sqlite_session = Session(bind=sqlite_engine)

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True)
    opening = Column('opening', Time)
    closing = Column('closing', Time)
    capacity = Column('capacity', Integer)


class Client(Base):
    __tablename__ = 'clients'

    client_id = Column(Integer, primary_key=True)
    name = Column('name', String)


class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True)
    id_room = Column('id_room', Integer, ForeignKey('rooms.room_id'))
    id_client = Column('id_client', Integer, ForeignKey('clients.client_id'))
    start = Column('start', DateTime)
    end = Column('end', DateTime)
    

Base.metadata.create_all(sqlite_engine)