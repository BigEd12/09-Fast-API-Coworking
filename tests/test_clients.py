
from fastapi.testclient import TestClient
from main import app
from database.db import Session
from database.models import Client

client = TestClient(app)


def test_clients_bookings_status_code():
    response = client.get('/api/clients/bookings')
    assert response.status_code == 200
        
def tst_clients_bookings_response_type():
    response = client.get('/api/clients/bookings')
    data = response.json()
    assert isinstance(data, dict)
        


