
from fastapi.testclient import TestClient
from main import app
from database.db import Session
from database.models import Client

client = TestClient(app)

class TestClientEndpoints:
    def test_clients_bookings(self):
        with Session() as session:  
            response = client.get('/api/clients/bookings')
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            
            clients = session.query(Client).all()
            if clients:
                assert 'No information found'
            else:
                assert 'Bookings per client' in data
        

    def test_client_content(self):
        with Session() as session:
            response = client.get('/api/clients/bookings')
            response_data = response.json()
            
            clients = session.query(Client).all()
            if clients:
                assert len(response_data) != 0
            else:
                assert len(response_data) == 0

