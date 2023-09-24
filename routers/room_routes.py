from datetime import datetime

from fastapi import APIRouter, Depends, Form, Query
from typing import Optional

from database.models import Room, Booking
from database.db import Session
from database.models import Booking

from utils.datetime.datetime import convert_time
from utils.overlap.overlap import check_overlap
from utils.usage.usage import calculate_percentage_per_room

router = APIRouter()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()
        
        
@router.get('/all')
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
    
@router.post('/add')
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


@router.get('/usage')
def get_rooms_usage(session: Session = Depends(get_db_session)):
    """
    Returns the percentage each room has been used

    Returns:
        dict: A dictionary indicating what percentage of the available time have the rooms been used
    """
    result = calculate_percentage_per_room(session)

    return {'Usage percentage by room': result}
    

@router.get('/availability/{room_id}/{timestamp}')
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
        

@router.get('/overlap')
def get_overlapping_bookings(session: Session = Depends(get_db_session)):
    """
    Returns all overlapping bookings.

    Returns:
        list: A list of dictionaries with all overlapping bookings
    """
    bookings = session.query(Booking).all()

    return check_overlap(bookings)