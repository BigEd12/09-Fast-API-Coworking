from fastapi import APIRouter, HTTPException, Depends, Form, Query
from typing import Optional
import re

from database.db import Session, get_db_session
from database.models import Booking, Client, Room

router = APIRouter()

@router.get('/')
async def get_all_bookings(session: Session = Depends(get_db_session))-> dict:
    """
    Gets all available bookings.

    This endpoint retrieves and returns all available booking records from the database.
    
    Returns:
        dict: A dictionary containing all available booking records.

    Raises:
        HTTPException (status_code=404):
            - If no booking information is found in the database. Try using the 'data/load' endpoint first.
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
    )-> dict:
    """
    Posts a new booking.

    This endpoint allows you to create a new booking with the specified room, client, and time slot.

    Parameters:
        - id_room (int): The ID of the room for the booking.
        - id_client (int): The ID of the client making the booking.
        - start (str): The start time of the booking in the format YYYY-MM-DDTHH:MMZ.
        - end (str): The end time of the booking in the format YYYY-MM-DDTHH:MMZ.

    Returns:
        dict: A dictionary containing the confirmed booking details.

    Raises:
        HTTPException (status_code=400):
            - If the 'start' or 'end' time is not in the correct format (YYYY-MM-DDTHH:MMZ).
        HTTPException (status_code=404):
            - If the specified 'id_client' or 'id_room' is not found in the database.

    Example:
        To make a booking for Room 3 by Client 3 from 2023-09-25T15:30Z to 2023-09-25T16:30Z:
        ```
        POST api/bookings/make
        Form Data:
        - id_room: 3
        - id_client: 3
        - start: 2023-09-25T15:30Z
        - end: 2023-09-25T16:30Z
        ```
    """
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z$'
    if not re.match(pattern, start):
        raise HTTPException(status_code=400, detail='Incorrect date format for start time')
    
    if not re.match(pattern, end):
        raise HTTPException(status_code=400, detail='Incorrect date format for end time')

    if not session.query(Client).filter(Client.client_id == id_client).first():
        raise HTTPException(status_code=404, detail=f'Client {id_client} not found.')
    
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
    client_id: Optional[int] = Query(None, description='Filter by client ID'),
    room_id: Optional[int] = Query(None, description='Filter by room ID'),
    session: Session = Depends(get_db_session)
    )-> dict:
    """
    Gets bookings with optional filters.

    This endpoint retrieves and returns booking records based on optional filters, including
    filtering by client ID and room ID.

    Parameters:
        - client_id (int, optional): Filter bookings by client ID.
        - room_id (int, optional): Filter bookings by room ID.

    Returns:
        dict: A list of bookings matching the specified filters.

    Raises:
        HTTPException (status_code=404):
            - If no bookings are found based on the specified filters.

    Example:
        To get all bookings for Client 3:
        ```
        GET api/bookings/filter?client_id=101
        ```

        To get all bookings for Room 3:
        ```
        GET api/bookings/filter?room_id=42
        ```

        To get all bookings for Client 3 in Room 3:
        ```
        GET api/bookings/filter?client_id=3&room_id=3
        ```
    """
    query = session.query(Booking)
    
    if client_id is not None:
        query = query.filter(Booking.id_client == client_id)
    if room_id is not None:
        query = query.filter(Booking.id_room == room_id)
            
    bookings = query.all()
    
    if not bookings:
        raise HTTPException(status_code=404, detail='ID not found')
    
    booking_list = [{'id_room': booking.id_room, 'id_client': booking.id_client, 'start': booking.start, 'end': booking.end} for booking in bookings]
    return booking_list
        