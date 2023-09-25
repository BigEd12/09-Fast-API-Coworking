from fastapi import APIRouter, HTTPException, Depends

from database.db import Session
from database.models import Booking, Client

router = APIRouter()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

@router.get('/bookings')
async def get_bookings_by_all_clients(session: Session = Depends(get_db_session)):
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
