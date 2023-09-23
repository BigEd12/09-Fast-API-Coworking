from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, Form
from starlette.responses import RedirectResponse

from database.models import Room, Client, Booking
from database.db import Session

from original_data.original_data import data

from utils.datetime.datetime import convert_time
from utils.overlap.overlap import check_overlap

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
    
@app.post('/bookings')
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

@app.get('/bookings/client/{client_id}')
def get_bookings_by_client(client_id: int,
                           session: Session = Depends(get_db_session)
                           ):
    """
    Returns all bookings made by a queried client

    Args:
        client_id (int): The client ID to check bookings for.

    Returns:
        dict: A dictionary with all bookings made by the queried client, if bookings or the client exist
    """
    try:
        if session.query(Client).filter(Client.client_id == client_id).first():
            bookings = session.query(Booking).filter(Booking.id_client == client_id).all()
            booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
        
            if booking_list:
                return {f'Bookings by client {client_id}': booking_list}
            else:
                return {f'Bookings by client {client_id}': 'No bookings found'}
        else:
            return {'Error': f'Client {client_id} not found'}
    except Exception as e:
        return {'error': str(e)}

@app.get('/bookings/room/{room_id}')
def get_bookings_by_room(
    room_id: int,
    session: Session = Depends(get_db_session)
    ):
    """
    Returns all bookings for a queried room

    Args:
        room_id (int): The ID of the room to check bookings for.
    
    Returns:
        dict: A dictionary indicating the bookings of a room if bookings or the room exist
    """
    try:
        if session.query(Room).filter(Room.room_id == room_id).first():
            bookings = session.query(Booking).filter(Booking.id_room == room_id).all()
            booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
            
            if len(booking_list) != 0:
                return {f'Bookings for room {room_id}': booking_list}
            else:
                return {f'Bookings for room {room_id}': 'No bookings found'}
        else:
            return {'Error': f'Room {room_id} not found'}
    except Exception as e:
        return {'error': str(e)}

# #----- ROOM ENDPOINTS -----#

@app.get('/rooms')
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
    
@app.post('/rooms')
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
    
    def room_open_hours():
        """
        Calculates how long each room is open in a day
        """
        rooms = session.query(Room).all()
        rooms_open_hours = {}
        for room in rooms:
            open_time = datetime.strptime(room.opening, "%H:%M")
            close_time = datetime.strptime(room.closing, "%H:%M")
            rooms_open_hours[room.room_id] = (close_time - open_time).total_seconds() / 3600
        return rooms_open_hours
    
    def total_days_in_range():
        """
        Calculates the number of days in the range of bookings
        """
        bookings = session.query(Booking).all()
        date_list = []
        for booking in bookings:
            date_list.append(convert_time(booking.start))
        unique_dates = set(date.date() for date in date_list)
        return len(unique_dates)
    
    def total_bookings_per_room():
        """
        Calculates total time each room was used
        """
        bookings = session.query(Booking).all()
        total_room_usage = {}
        for booking in bookings:
            room_id = booking.id_room
            start = datetime.strptime(convert_time(booking))
            end = datetime.strptime(convert_time(booking.end))
            booking_time = end - start

            if room_id not in total_room_usage:
                total_room_usage[room_id] = booking_time
            else:
                total_room_usage[room_id] += booking_time
        return total_room_usage
    
    def total_open_hours_per_room():
        """
        Calculates total time each room is open
        """
        open_hours = {}
        rooms_open_hours = room_open_hours()
        num_unique_dates = total_days_in_range()
        for key, value in rooms_open_hours.items():
            open_hours[key] = timedelta(hours=value * num_unique_dates)
        return open_hours
    
    def calculate_percentage_per_room():
        """
        Calculates time room was used against open as a percentage
        """
        bookings_per_room = total_bookings_per_room()
        open_hours_per_room = total_open_hours_per_room()
        percentage_dict = {}
        
        for room_id, timedelta1 in open_hours_per_room.items():
            if room_id in bookings_per_room:
                timedelta2 = bookings_per_room[room_id]
                if timedelta1.total_seconds() == 0:
                    percentage = 0.0
                else:
                    percentage = round((timedelta2.total_seconds() / timedelta1.total_seconds()) * 100, 0)
            else:
                percentage = 0.0
            
            percentage_dict[room_id] = f'{percentage}%'
        
        return percentage_dict

    result = calculate_percentage_per_room()

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
        

@app.get('/rooms/bookings/overlapping')
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
    