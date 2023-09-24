from fastapi import APIRouter, HTTPException, Depends, Form, Query
from typing import Optional
import re

from database.db import Session
from database.models import Booking, Client, Room

router = APIRouter()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

@router.get('/')
async def get_all_bookings(session: Session = Depends(get_db_session)):
    """
    Returns all bookings

    Returns:
        dict: A dictionary with all bookings
    """
    bookings = session.query(Booking).all()
    if not bookings:
        raise HTTPException(status_code=404, detail='No booking information found. Try using data/load root first.')
    return {"All bookings": bookings}
    
@router.post('/make')
async def make_new_booking(
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
        id_client (int): The ID of the client making the booking.
        start (str): The start time of the booking (HH:MM).
        end (str): The end time of the booking (HH:MM).

    Returns:
        dict: A dictionary with all the confirmed bookings.
    """
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$'
    if not re.match(pattern, start):
        raise HTTPException(status_code=400, detail='Incorrect date format for start time')
    
    if not re.match(pattern, end):
        raise HTTPException(status_code=400, detail='Incorrect date format for end time')

    clients = session.query(Client).all()
    if not session.query(Client).filter(Client.client_id == id_client).first():
        raise HTTPException(status_code=404, detail=f'Client {id_client} not found.')
    
    rooms = session.query(Room).all()
    if not session.query(Room).filter(Room.room_id == id_room).first():
        raise HTTPException(status_code=404, detail=f'Room {id_room} not found.')

    new_booking = Booking(
        id_room=id_room,
        id_client=id_client,
        start=start, end=end
        )
    
    session.add(new_booking)
    session.commit()
    added_booking = session.query(Booking).filter(Booking.id == new_booking.id).first()
    
    return {'Booking confirmed': added_booking}

@router.get('/filter')
async def get_bookings_by_filter(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    session: Session = Depends(get_db_session)
):
    """
    Returns bookings with optional filters

    Args:
        client_id (int, optional): The client ID to filter by.
        room_id (int, optional): The room ID to filter by.

    Returns:
        dict: A dictionary with all bookings filtered by client or room.
    """
    query = session.query(Booking)
    
    if client_id is not None:
        query = query.filter(Booking.id_client == client_id)
    if room_id is not None:
        query = query.filter(Booking.id_room == room_id)
            
    bookings = query.all()
    
    if not bookings:
        raise HTTPException(status_code=404, detail="ID not found")
    
    booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
    return booking_list
        