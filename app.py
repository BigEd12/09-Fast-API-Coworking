from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

sqlite_url = "sqlite:///coworking.db"
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
    start = Column('start', String)
    end = Column('end', String)
    

Base.metadata.create_all(sqlite_engine)


data = {
    "rooms": [
		{ "id": 1, "opening": "08:00", "closing": "20:00", "capacity": 4 },
		{ "id": 2, "opening": "08:00", "closing": "14:00", "capacity": 10 },
		{ "id": 3, "opening": "10:00", "closing": "18:00", "capacity": 6 }
	],
    "clients": [
		{ "id": 1, "name": "Client 1" },
		{ "id": 2, "name": "Client 2" },
		{ "id": 3, "name": "Client 3" },
		{ "id": 4, "name": "Client 4" },
		{ "id": 5, "name": "Client 5" },
		{ "id": 6, "name": "Client 6" },
		{ "id": 7, "name": "Client 7" }
	],
    "bookings": [
		{
			"id_room": 1,
			"id_client": 1,
			"start": "2023-07-18T10:00Z",
			"end": "2023-07-18T12:00Z"
		},
		{
			"id_room": 1,
			"id_client": 2,
			"start": "2023-07-18T12:00Z",
			"end": "2023-07-18T18:00Z"
		},
		{
			"id_room": 1,
			"id_client": 3,
			"start": "2023-07-18T17:00Z",
			"end": "2023-07-18T20:00Z"
		},
		{
			"id_room": 2,
			"id_client": 4,
			"start": "2023-07-18T12:00Z",
			"end": "2023-07-18T14:00Z"
		},
		{
			"id_room": 3,
			"id_client": 5,
			"start": "2023-07-18T10:00Z",
			"end": "2023-07-18T18:00Z"
		},
		{
			"id_room": 1,
			"id_client": 6,
			"start": "2023-07-19T10:00Z",
			"end": "2023-07-19T12:00Z"
		},
		{
			"id_room": 2,
			"id_client": 6,
			"start": "2023-07-19T11:00Z",
			"end": "2023-07-19T12:00Z"
		},
		{
			"id_room": 1,
			"id_client": 7,
			"start": "2023-07-20T10:00Z",
			"end": "2023-07-20T20:00Z"
		},
		{
			"id_room": 1,
			"id_client": 4,
			"start": "2023-07-20T10:00Z",
			"end": "2023-07-20T12:00Z"
		},
		{
			"id_room": 2,
			"id_client": 3,
			"start": "2023-07-20T08:00Z",
			"end": "2023-07-20T14:00Z"
		},
		{
			"id_room": 3,
			"id_client": 2,
			"start": "2023-07-20T10:00Z",
			"end": "2023-07-20T14:00Z"
		},
		{
			"id_room": 3,
			"id_client": 6,
			"start": "2023-07-20T14:00Z",
			"end": "2023-07-20T18:00Z"
		},
		{
			"id_room": 1,
			"id_client": 1,
			"start": "2023-07-21T08:00Z",
			"end": "2023-07-21T09:00Z"
		},
		{
			"id_room": 1,
			"id_client": 2,
			"start": "2023-07-21T09:00Z",
			"end": "2023-07-21T10:00Z"
		},
		{
			"id_room": 1,
			"id_client": 3,
			"start": "2023-07-21T10:00Z",
			"end": "2023-07-21T11:00Z"
		},
		{
			"id_room": 1,
			"id_client": 4,
			"start": "2023-07-21T11:00Z",
			"end": "2023-07-21T12:00Z"
		},
		{
			"id_room": 1,
			"id_client": 5,
			"start": "2023-07-21T12:00Z",
			"end": "2023-07-21T13:00Z"
		},
		{
			"id_room": 1,
			"id_client": 6,
			"start": "2023-07-21T13:00Z",
			"end": "2023-07-21T14:00Z"
		},
		{
			"id_room": 1,
			"id_client": 7,
			"start": "2023-07-21T14:00Z",
			"end": "2023-07-21T15:00Z"
		}
	]
}

try:
    for room_data in data.get("rooms", []):
        room_data["room_id"] = room_data.pop("id")
        room_data["opening"] = datetime.strptime(room_data["opening"], "%H:%M").time()
        room_data["closing"] = datetime.strptime(room_data["closing"], "%H:%M").time()
        room = Room(**room_data)
        sqlite_session.add(room)

    for client_data in data.get("clients", []):
        client_data["client_id"] = client_data.pop("id")
        client = Client(**client_data)
        sqlite_session.add(client)

    for booking_data in data.get("bookings", []):
        booking = Booking(**booking_data)
        sqlite_session.add(booking)
        

    sqlite_session.commit()
    print("Data added to the database successfully.")
except Exception as e:
    sqlite_session.rollback()
    print(f"Error: {e}")
finally:
    sqlite_session.close()
