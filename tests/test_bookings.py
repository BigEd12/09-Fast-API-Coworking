from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_bookings_response_code():
    response = client.get('/api/bookings')
    assert response.status_code == 200
    
def test_get_all_bookings_response_type():
    response = client.get('/api/bookings')
    response_data = response.json()
    assert isinstance(response_data, dict)

def test_make_new_booking_error_response_code():
    data = {
        "id_room": 0,
        "id_client": 1,
        "start": "2023-09-24T12:00Z",
        "end": "2023-09-24T14:00Z",
    }
    response = client.post('/api/bookings/make', data=data)
    assert response.status_code == 404
    

def test_get_bookings_by_filter_response_code():
    params = {
        "client_id": 1,
        "room_id": 1,
    }
    response = client.get('/api/bookings/filter', params=params)
    assert response.status_code == 200
    
def test_get_bookings_by_filter_error_response_code():
    params = {
        "client_id": 0,
        "room_id": 0,
    }
    response = client.get('/api/bookings/filter', params=params)
    assert response.status_code == 404
    
def test_get_bookings_by_filter_response_type():
    params = {
        "client_id": 3,
    }
    response = client.get('/api/bookings/filter', params=params)
    response_data = response.json()
    assert isinstance(response_data, list)
