from fastapi.testclient import TestClient
from main import app

from database.db import Session
from database.models import Client

client = TestClient(app)

def test_client_response_code():
    response = client.get('/api/clients/bookings')
    assert response.status_code == 200

def test_client_response_type():
    response = client.get('/api/clients/bookings')
    response_data = response.json()
    assert isinstance(response_data, dict)

def test_client_content():
    with Session() as session:
        response = client.get('/api/clients/bookings')
        response_data = response.json()
        
        clients = session.query(Client).all()
        if clients:
            assert len(response_data) != 0
        else:
            assert len(response_data) == 0