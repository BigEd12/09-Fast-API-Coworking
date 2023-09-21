from fastapi import FastAPI, Depends, Form
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
    
@app.post('/bookings')
def make_new_booking(
    id_room: int = Form(...),
    id_client: int = Form(...),
    start: str = Form(...),
    end: str = Form(...),
    session: Session = Depends(get_db_session)
    ):

    try:
        new_booking = Booking(id_room=id_room, id_client=id_client, start=start, end=end)
        session.add(new_booking)
        session.commit()
        
        added_booking = session.query(Booking).filter(Booking.id == new_booking.id).first()
        
        return {'message': 'new booking made successfully', 'new booking': added_booking }
    except Exception as e:
        return {"error": str(e)}

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
        rooms = session.query(Room).all()
        room_list = [{"room_id": room.room_id, "opening": room.opening, "closing": room.closing, "capacity": room.capacity} for room in rooms]
        
        return {"rooms": room_list}
    except Exception as e:
        return {"error": str(e)}
    
@app.post('/rooms')
def add_new_room(
    opening: str = Form(...),
    closing: str = Form(...),
    capacity: int = Form(...),
    session: Session = Depends(get_db_session)
    ):

    try:
        opening_time = datetime.strptime(opening, "%H:%M").time()
        closing_time = datetime.strptime(closing, "%H:%M").time()
        
        new_room = Room(opening=opening_time, closing=closing_time, capacity=capacity)
        session.add(new_room)
        session.commit()
        
        added_room = session.query(Room).filter(Room.room_id == new_room.room_id).first()
        
        return {'message': 'new room added successfully', 'new room': added_room }
    except Exception as e:
        return {"error": str(e)}


# @app.get('/rooms/usage')
# def get_rooms_usage():
#     return pass

@app.get('/rooms/availability/{room_id}/{timestamp}')
def check_room_availability(room_id: int, timestamp: str, session: Session = Depends(get_db_session)):
    bookings = session.query(Booking).filter(Booking.id_room == room_id).all()
    date_format = "%Y-%m-%d %H:%M"
    query = datetime.strptime(timestamp.split('T')[0] + ' ' + timestamp.split('T')[1][:-1], date_format)
    
    for booking in bookings:
        start = booking.start
        end = booking.end
        start_date_time = datetime.strptime(start.split('T')[0] + ' ' + start.split('T')[1][:-1], date_format)
        end_date_time = datetime.strptime(end.split('T')[0] + ' ' + end.split('T')[1][:-1], date_format)
        
        if start_date_time <= query <= end_date_time:
            return {f'message': f'room {room_id} busy at the requested time({query})'}
        
    return {f'message': f'room {room_id} available at the requested time({query})'}
        

# @app.get('/rooms/bookings/overlapping')
# def get_overlapping_bookings():
#     return pass

# #----- CLIENT ENDPOINT -----#

@app.get('/clients/bookings')
def get_bookings_by_all_clients(session: Session = Depends(get_db_session)):
    try:
        client_ids = []
        client_count = {}
        bookings = session.query(Booking)
        for booking in bookings:
            client_ids.append(booking.id_client)
            
        for client_id in client_ids:
            if client_id in client_count:
                client_count[client_id] += 1
            else:
                client_count[client_id] = 1
        return {'bookings per client': client_count}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": "Internal Server Error"}
    