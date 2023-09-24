from fastapi import APIRouter, Depends

from database.db import Session
from database.models import Booking

router = APIRouter()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

@router.get('/bookings')
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