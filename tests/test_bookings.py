from fastapi import Depends
from fastapi.testclient import TestClient

from database.db import Session
from database.models import Booking

from main import app

client = TestClient(app)

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

def test_bookings_response_code():
    response = client.get('/api/bookings')
    assert response.status_code == 200

def test_booking_response_type():
    response = client.get('/api/bookings')
    response_data = response.json()
    assert isinstance(response_data, dict)
    
def test_booking_content():
    with Session() as session:
        response = client.get('/api/bookings')
        response_data = response.json()
        
        bookings = session.query(Booking).all()
        if bookings:
            assert len(response_data) != 0
        else:
            assert len(response_data) == 0