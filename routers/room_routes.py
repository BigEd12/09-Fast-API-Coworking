import re
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Depends, Form 

from database.models import Room, Booking
from database.db import Session, get_db_session

from utils.datetime import convert_time
from utils.overlap import check_overlap
from utils.usage import calculate_percentage_per_room

router = APIRouter()

        
@router.get('/all')
async def get_all_rooms(session: Session = Depends(get_db_session)) -> Dict[str, List]:
    """
    Gets information on all rooms.
    """
    rooms = session.query(Room).all()
    
    if not rooms:
        raise HTTPException(status_code=404, detail='No room information found. Try using data/load root first.')
    room_list = [{'room_id': room.room_id, 'opening': room.opening, 'closing': room.closing, 'capacity': room.capacity} for room in rooms]
    
    return {'Rooms': room_list}

    
@router.post('/add')
async def add_new_room(
    opening: str = Form(..., description='Opening time of new room (HH:MM)'),
    closing: str = Form(..., description='Closing time of new room (HH:MM)'),
    capacity: int = Form(..., description='Capacity of new room'),
    session: Session = Depends(get_db_session)
    )-> Dict[str, Dict]:
    """
    Add a new room.
    """
    pattern = r'^\d{2}:\d{2}$'
    if not re.match(pattern, opening):
        raise HTTPException(status_code=400, detail='Incorrect time format for opening time.')
    
    if not re.match(pattern, closing):
        raise HTTPException(status_code=400, detail='Incorrect time format for closing time.')
    
    if capacity == '0':
        raise HTTPException(status_code=400, detail='Room with 0 capacity cannot be added.')
    
    new_room = Room(opening=opening, closing=closing, capacity=capacity)
    session.add(new_room)
    session.commit()
    
    added_room = session.query(Room).filter(Room.room_id == new_room.room_id).first()
    
    return {'Room added': added_room}



@router.get('/usage')
async def get_rooms_usage(session: Session = Depends(get_db_session)) -> Dict[str, Dict]:
    """
    Gets the percentage each room has been used in the time available.
    """
    bookings = session.query(Booking).all()
    
    if not bookings:
        raise HTTPException(status_code=404, detail='No booking information found. Try using data/load root first.')
    
    result = calculate_percentage_per_room(session)

    return {'Usage percentage by room': result}
    

@router.get('/availability/{room_id}/{timestamp}')
async def check_room_availability(
    room_id: int,
    timestamp: str,
    session: Session = Depends(get_db_session)
    ) -> Dict[str, str]:
    """
    Gets queried room availability at the queried timestamp.

    Parameters:
    - room_id (int): The ID of the room you want to check availability for.
    - timestamp (str): The timestamp for which you want to check availability (in YYYY-MM-DDTHH:MMZ format).

    """
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$'
    if not re.match(pattern, timestamp):
        raise HTTPException(status_code=400, detail='Incorrect time format.')
    
    bookings = session.query(Booking).filter(Booking.id_room == room_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail=f'Room {room_id} not found.')
    
    query = convert_time(timestamp)
    
    for booking in bookings:
        start = booking.start
        end = booking.end
        start_date_time = convert_time(start)
        end_date_time = convert_time(end)
        
        if start_date_time <= query <= end_date_time:
            return {f'Room {room_id}': f'Busy at requested time({query})'}
        
    return {f'Room {room_id}': f'Available at requested time({query})'}
        

@router.get('/overlap')
async def get_overlapping_bookings(session: Session = Depends(get_db_session)) -> Dict[str, List]:
    """
    Gets all overlapping bookings.
    """
    bookings = session.query(Booking).all()
    
    if not bookings:
        raise HTTPException(status_code=404, detail='No booking information found. Try using data/load root first.')

    return check_overlap(bookings)