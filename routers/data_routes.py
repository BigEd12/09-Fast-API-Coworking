from fastapi import APIRouter, Depends

from database.db import Session, get_db_session
from database.models import Booking, Client, Room

from original_data.original_data import data

router = APIRouter()

        
@router.post('/load')
async def load_initial_data(session: Session = Depends(get_db_session))-> dict:
    """
    Populates the database with initial data if it is empty.

    This endpoint checks if the database is empty and, if so, populates it with initial data.
    The data includes rooms, clients, and bookings. If the database already contains data,
    it returns a message indicating that the database is already populated.

    Returns:
        dict: A message indicating the result of the data population process.
    """
    if (
        session.query(Room).count() == 0 and
        session.query(Client).count() == 0 and
        session.query(Booking).count() == 0
    ):
        for room_data in data.get('rooms', []):
            room_data['room_id'] = room_data.pop('id')
            room_data['opening'] = room_data['opening']
            room_data['closing'] = room_data['closing']
            room = Room(**room_data)
            session.add(room)

        for client_data in data.get('clients', []):
            client_data['client_id'] = client_data.pop('id')
            client = Client(**client_data)
            session.add(client)

        for booking_data in data.get('bookings', []):
            booking = Booking(**booking_data)
            session.add(booking)

        session.commit()
        return {'message': 'Data added to the database successfully.'}
    else:
        return {'message': 'Database is already populated.'}