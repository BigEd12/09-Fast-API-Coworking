from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_client_response_type():
    response = client.get('api/clients/bookings')
    assert response.status_code == 200
