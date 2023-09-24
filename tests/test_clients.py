
from fastapi.testclient import TestClient
from main import app
from database.db import Session
from database.models import Client

client = TestClient(app)

class TestClientEndpoints:
    def test_client_response_code(self):
        response = client.get('/api/clients/bookings')
        assert response.status_code == 200

    def test_client_response_type(self):
        response = client.get('/api/clients/bookings')
        response_data = response.json()
        assert isinstance(response_data, dict)

    def test_client_content(self):
        # Assuming you have created some sample clients in your test database
        with Session() as session:
            response = client.get('/api/clients/bookings')
            response_data = response.json()
            
            clients = session.query(Client).all()
            if clients:
                assert len(response_data) != 0
            else:
                assert len(response_data) == 0

