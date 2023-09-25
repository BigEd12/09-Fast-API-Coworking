from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_rooms_status_code():
    response = client.get('/api/rooms/all')
    assert response.status_code == 200
    
def test_get_all_rooms_response_type():
    response = client.get('/api/rooms/all')
    data = response.json()
    assert isinstance(data, dict)

def test_add_new_room_response_error_code():
    data = [
        {'opening': 't8:00', 'closing': '17:00', 'capacity': '10'},
        {'opening': '08:00', 'closing': '17:00', 'capacity': '0'},
        {'opening': '08:00', 'closing': '17-00', 'capacity': '10'}
        ]
    for test_item in data:
        response = client.post('/api/rooms/add', data=test_item)
        assert response.status_code == 400
    
def test_get_rooms_usage_status_code():
    response = client.get('/api/rooms/usage')
    assert response.status_code == 200
    
def test_get_rooms_usage_response_type():
    response = client.get('/api/rooms/usage')
    data = response.json()
    assert isinstance(data, dict)

def test_check_room_availability_status_code():
    response = client.get('/api/rooms/availability/1/2023-09-01T10:00Z')
    assert response.status_code == 200

def test_check_room_availablility_response_type():
    response = client.get('/api/rooms/availability/1/2023-09-01T10:00Z')
    data = response.json()
    assert isinstance(data, dict)

def test_get_overlapping_bookings_status_code():
    response = client.get('/api/rooms/overlap')
    assert response.status_code == 200
    
def test_get_overlapping_bookings_response_type():
    response = client.get('/api/rooms/overlap')
    data = response.json()
    assert isinstance(data, dict)
