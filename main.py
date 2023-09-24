from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, Form, Query
from starlette.responses import RedirectResponse
from typing import Optional

from database.models import Room, Client, Booking
from database.db import Session

from original_data.original_data import data

from utils.datetime.datetime import convert_time
from utils.overlap.overlap import check_overlap
from utils.usage.usage import calculate_percentage_per_room

app = FastAPI()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

#----- INDEX / DOCS ENDPOINT -----#
@app.get('/')
def index():
    return RedirectResponse(url='/docs')


#----- INITIAL DATA ENDPOINT -----#

@app.post('/data/load')
def load_initial_data(session: Session = Depends(get_db_session)):
    """
    Populates database with initial load data if empty
    """
    try:
        if (
            session.query(Room).count() == 0 and
            session.query(Client).count() == 0 and
            session.query(Booking).count() == 0
        ):
            for room_data in data.get("rooms", []):
                room_data["room_id"] = room_data.pop("id")
                room_data["opening"] = room_data["opening"]
                room_data["closing"] = room_data["closing"]
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
        else:
            return {'message': 'Database is already populated.'}
    except Exception as e:
        return {"error": str(e)}

#----- BOOKING ENDPOINTS -----#

@app.get('/bookings')
def get_all_bookings(session: Session = Depends(get_db_session)):
    """
    Returns all bookings

    Returns:
        dict: A dictionary with all bookings
    """
    try:
        bookings = session.query(Booking).all()
        return {"All bookings": bookings}
    except Exception as e:
        return {"error": str(e)}
    
@app.post('/bookings/make')
def make_new_booking(
    id_room: int = Form(..., description='Room Id'),
    id_client: int = Form(..., description='Client Id'),
    start: str = Form(..., description='Booking start time (YYYY-MM-DDTHH:MMZ - Where "T" and "Z" remain unchanged)'),
    end: str = Form(..., description='Booking end time (YYYY-MM-DDTHH:MMZ - Where "T" and "Z" remain unchanged)'),
    session: Session = Depends(get_db_session)
    ):
    """
    Makes a new booking

    Args:
        id_room (int): The room ID where the booking is for.
        client_id (int): The ID of the client making the booking.
        start (str): The start time of the booking (HH:MM).
        end (str): The end time of the booking (HH:MM).

    Returns:
        dict: A dictionary with all the confirmed booking.
    """

    try:
        new_booking = Booking(
            id_room=id_room,
            id_client=id_client,
            start=start, end=end
            )
        
        session.add(new_booking)
        session.commit()
        added_booking = session.query(Booking).filter(Booking.id == new_booking.id).first()
        
        return {'Booking confirmed': added_booking}
    except Exception as e:
        return {"error": str(e)}

@app.get('/bookings/filter')
def get_bookings_by_filter(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    session: Session = Depends(get_db_session)
):
    """
    Returns bookings with optional filters.

    Args:
        client_id (int, optional): The client ID to filter by.
        room_id (int, optional): The room ID to filter by.

    Returns:
        dict: A dictionary with all bookings filtered by client or room.
    """
    try:
        query = session.query(Booking)
        
        if client_id is not None:
            query = query.filter(Booking.id_client == client_id)
        if room_id is not None:
            query = query.filter(Booking.id_room == room_id)
        
        bookings = query.all()
        
        if not bookings:
            return {"message": "No bookings found"}
        
        booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
        return booking_list
        
    except Exception as e:
        return {"error": str(e)}

# #----- ROOM ENDPOINTS -----#

@app.get('/rooms/all')
def get_all_rooms(session: Session = Depends(get_db_session)):
    """
    Returns information on all rooms

    Returns:
        list: A list of dictionaries with information on each room
    """
    try:
        rooms = session.query(Room).all()
        room_list = [{"room_id": room.room_id, "opening": room.opening, "closing": room.closing, "capacity": room.capacity} for room in rooms]
        
        return {"Rooms": room_list}
    except Exception as e:
        return {"error": str(e)}
    
@app.post('/rooms/add')
def add_new_room(
    opening: str = Form(..., description='Opening time of new room (HH:MM)'),
    closing: str = Form(..., description='Closing time of new room (HH:MM)'),
    capacity: int = Form(..., description='Capacity of new room'),
    session: Session = Depends(get_db_session)
    ):
    """
    Add a new room
    """
    try:        
        new_room = Room(opening=opening, closing=closing, capacity=capacity)
        session.add(new_room)
        session.commit()
        
        added_room = session.query(Room).filter(Room.room_id == new_room.room_id).first()
        
        return {'Room added': added_room}
    except Exception as e:
        return {"error": str(e)}


@app.get('/rooms/usage')
def get_rooms_usage(session: Session = Depends(get_db_session)):
    """
    Returns the percentage each room has been used

    Returns:
        dict: A dictionary indicating what percentage of the available time have the rooms been used
    """
    result = calculate_percentage_per_room(session)

    return {'Usage percentage by room': result}
    

@app.get('/rooms/availability/{room_id}/{timestamp}')
def check_room_availability(
    room_id: int,
    timestamp: str,
    session: Session = Depends(get_db_session)
    ):
    """
    Returns queried room availability at the queried timestamp

    Args:
        room_id (int): The ID of the room to check availability for.
        timestamp (str): The timestamp to check availability at (YYYY-MM-DDTHH:MMZ - Where "T" and "Z" remain unchanged).

    Returns:
        dict: A dictionary indicating whether the room is busy or available at the requested time.
    """
    bookings = session.query(Booking).filter(Booking.id_room == room_id).all()
    date_format = "%Y-%m-%d %H:%M"
    query = datetime.strptime(convert_time(timestamp))
    
    for booking in bookings:
        start = booking.start
        end = booking.end
        start_date_time = datetime.strptime(convert_time(start))
        end_date_time = datetime.strptime(convert_time(end))
        
        if start_date_time <= query <= end_date_time:
            return {f'Room {room_id}': f'Busy at requested time({query})'}
        
    return {f'Room {room_id}': f'Available at requested time({query})'}
        

@app.get('/rooms/overlapping')
def get_overlapping_bookings(session: Session = Depends(get_db_session)):
    """
    Returns all overlapping bookings.

    Returns:
        list: A list of dictionaries with all overlapping bookings.
    """
    bookings = session.query(Booking).all()

    return check_overlap(bookings)
    
# #----- CLIENT ENDPOINT -----#

@app.get('/clients/bookings')
def get_bookings_by_all_clients(session: Session = Depends(get_db_session)):
    """
    Returns all bookings made by all clients.

    Returns:
        dict: A dictionary with all bookings made by each client.
    """
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
        return {'Bookings per client': client_count}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": "Internal Server Error"}
    