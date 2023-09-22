from fastapi import FastAPI, Depends, Form
from datetime import datetime
from datetime import timedelta

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
def load_initial_data(session: Session = Depends(get_db_session)):
    try:
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


@app.get('/rooms/usage')
def get_rooms_usage(session: Session = Depends(get_db_session)):
    
    def room_open_hours():
        rooms = session.query(Room).all()
        rooms_open_hours = {}
        for room in rooms:
            open_time = datetime.strptime(room.opening, "%H:%M")
            close_time = datetime.strptime(room.closing, "%H:%M")
            rooms_open_hours[room.room_id] = (close_time - open_time).total_seconds() / 3600  # Convert to hours
        return rooms_open_hours
    
    def total_days_in_range():
        bookings = session.query(Booking).all()
        date_list = []
        for booking in bookings:
            date_list.append(datetime.strptime(booking.start.split('T')[0] + ' ' + booking.start.split('T')[1][:-1], '%Y-%m-%d %H:%M'))
        unique_dates = set(date.date() for date in date_list)
        return len(unique_dates)
    
    def total_bookings_per_room():
        bookings = session.query(Booking).all()
        total_room_usage = {}
        for booking in bookings:
            room_id = booking.id_room
            start = datetime.strptime(booking.start.split('T')[0] + ' ' + booking.start.split('T')[1][:-1], "%Y-%m-%d %H:%M")
            end = datetime.strptime(booking.end.split('T')[0] + ' ' + booking.end.split('T')[1][:-1], "%Y-%m-%d %H:%M")
            booking_time = end - start

            if room_id not in total_room_usage:
                total_room_usage[room_id] = booking_time
            else:
                total_room_usage[room_id] += booking_time
        return total_room_usage
    
    def total_open_hours_per_room():
        open_hours = {}
        rooms_open_hours = room_open_hours()
        num_unique_dates = total_days_in_range()
        for key, value in rooms_open_hours.items():
            open_hours[key] = timedelta(hours=value * num_unique_dates)
        return open_hours
    
    def calculate_percentage_per_room():
        bookings_per_room = total_bookings_per_room()
        open_hours_per_room = total_open_hours_per_room()
        percentage_dict = {}
        for room_id, timedelta1 in bookings_per_room.items():
            if room_id in open_hours_per_room:
                timedelta2 = open_hours_per_room[room_id]
                if timedelta2.total_seconds() == 0:
                    percentage = 0.0
                else:
                    percentage = (timedelta1.total_seconds() / timedelta2.total_seconds()) * 100
                percentage_dict[room_id] = percentage
        return percentage_dict

    result = calculate_percentage_per_room()

    return {'message': result}
    
    
        
        

    

    
    
    


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
        

@app.get('/rooms/bookings/overlapping')
def get_overlapping_bookings(session: Session = Depends(get_db_session)):
    bookings = session.query(Booking).all()
    
    def overlap(booking1, booking2):
        if booking1.id_room != booking2.id_room:
            return False
        else:
            date_format = "%Y-%m-%d %H:%M"
            start1 = booking1.start
            end1 = booking1.end
            start2 = booking2.start
            end2 = booking2.end
            start1_date_time = datetime.strptime(start1.split('T')[0] + ' ' + start1.split('T')[1][:-1], date_format)
            end1_date_time = datetime.strptime(end1.split('T')[0] + ' ' + end1.split('T')[1][:-1], date_format)
            start2_date_time = datetime.strptime(start2.split('T')[0] + ' ' + start2.split('T')[1][:-1], date_format)
            end2_date_time = datetime.strptime(end2.split('T')[0] + ' ' + end2.split('T')[1][:-1], date_format)
            return start1_date_time < end2_date_time and start2_date_time < end1_date_time

    overlapping_bookings = []

    for i, booking1 in enumerate(bookings):
        for j, booking2 in enumerate(bookings):
            if i != j and overlap(booking1, booking2):
                overlapping_bookings.append((booking1, booking2))
    
    if len(overlapping_bookings) == 0:
        return {'message': 'No overlapping bookings'}
    else:
        overlapping_list = []
        for booking_pair in overlapping_bookings:
            overlapping_dict = {
                'booking1': booking_pair[0],
                'booking2': booking_pair[1]
            }
            overlapping_list.append(overlapping_dict)
        
        return {'message': 'Overlapping bookings found', 'overlapping_bookings': overlapping_list}

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
    