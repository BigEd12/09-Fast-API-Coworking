from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True)
    opening = Column('opening', String)
    closing = Column('closing', String)
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
    start = Column('start', String)
    end = Column('end', String)
    
