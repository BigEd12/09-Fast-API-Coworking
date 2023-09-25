from fastapi import APIRouter, HTTPException, Depends

from database.db import Session, get_db_session
from database.models import Booking

router = APIRouter()


@router.get('/bookings')
async def get_bookings_by_all_clients(session: Session = Depends(get_db_session))-> dict:
    """
    Returns all bookings made by all clients.

    Returns:
        dict: A dictionary with all bookings made by each client.
    """
    bookings = session.query(Booking)
    if not bookings:
        raise HTTPException(status_code=404, detail='No information found. Try using data/load route first.')
    
    client_ids = []
    client_count = {}
    for booking in bookings:
        client_ids.append(booking.id_client)
        
    for client_id in client_ids:
        if client_id in client_count:
            client_count[client_id] += 1
        else:
            client_count[client_id] = 1
    return {'Bookings per client': client_count}
