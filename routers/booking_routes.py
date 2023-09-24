from fastapi import APIRouter, Depends, Form, Query
from typing import Optional

from database.db import Session
from database.models import Booking

router = APIRouter()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

@router.get('/')
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
    
@router.post('/make')
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

@router.get('/filter')
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