from fastapi import FastAPI, Depends
from datetime import datetime

from database.models import Room, Client, Booking
from database.db import Session

from original_data.original_data import data

app = FastAPI()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

#----- INITIAL DATA ENDPOINT -----#

@app.post('/data/load')
def load_initial_data():
    try:
        with Session() as session:
            for room_data in data.get("rooms", []):
                room_data["room_id"] = room_data.pop("id")
                room_data["opening"] = datetime.strptime(room_data["opening"], "%H:%M").time()
                room_data["closing"] = datetime.strptime(room_data["closing"], "%H:%M").time()
                room = Room(**room_data)
                session.add(room)

            for client_data in data.get("clients", []):
                client_data["client_id"] = client_data.pop("id")
                client = Client(**client_data)
                session.add(client)

            for booking_data in data.get("bookings", []):
                booking = Booking(**booking_data)
                session.add(booking)

            session.commit()
        return {"message": "Data added to the database successfully."}
    except Exception as e:
        return {"error": str(e)}

#----- BOOKING ENDPOINTS -----#

@app.get('/bookings')
def get_all_bookings(session: Session = Depends(get_db_session)):
    try:
        bookings = session.query(Booking).all()
        booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
        
        return {"bookings": booking_list}
    except Exception as e:
        return {"error": str(e)}
    
# @app.post('/bookings')
# def make_new_booking():
#     return pass

@app.get('/bookings/client/{client_id}')
def get_bookings_by_client(client_id: int, session: Session = Depends(get_db_session)):
    try:
        bookings = session.query(Booking).filter(Booking.id_client == client_id).all()
        booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
    
        return {f'bookings by client {client_id}': booking_list}
    except Exception as e:
        return {'error': str(e)}

@app.get('/bookings/room/{room_id}')
def get_bookings_by_room(room_id: int, session: Session = Depends(get_db_session)):
    try:
        bookings = session.query(Booking).filter(Booking.id_room == room_id).all()
        booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
    
        return {f'bookings for room {room_id}': booking_list}
    except Exception as e:
        return {'error': str(e)}

# #----- ROOM ENDPOINTS -----#

@app.get('/rooms')
def get_all_rooms(session: Session = Depends(get_db_session)):
    try:
        # Query all rooms from the Room table using the provided session
        rooms = session.query(Room).all()
        # Convert the rooms to a list of dictionaries
        room_list = [{"room_id": room.room_id, "opening": room.opening, "closing": room.closing, "capacity": room.capacity} for room in rooms]
        return {"rooms": room_list}
    except Exception as e:
        return {"error": str(e)}
    
# @app.post('/rooms')
# def add_new_room():
#     return pass

# @app.get('/rooms/usage')
# def get_rooms_usage():
#     return pass

# @app.get('/rooms/availability/{room_id}/{timestamp}')
# def check_room_availability():
#     return pass

# @app.get('/rooms/bookings/overlapping')
# def get_overlapping_bookings():
#     return pass

# #----- CLIENT ENDPOINT -----#

# @app.get('/clients/bookings')
# def get_bookings_by_all_clients():
#     return pass