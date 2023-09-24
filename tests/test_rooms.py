from fastapi.testclient import TestClient
from main import app
from database.db import Session
from database.models import Room, Booking

client = TestClient(app)

class TestRoomEndpoints:
    def test_get_all_rooms(self):
        response = client.get('/api/rooms/all')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Rooms" in data

    def test_add_new_room(self):
        response = client.post('/api/rooms/add', data={"opening": '08:00', "closing": "17:00", "capacity": 10})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Room added" in data

    def test_get_rooms_usage(self):
        response = client.get('/api/rooms/usage')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Usage percentage by room" in data

    def test_check_room_availability(self):
        response = client.get('/api/rooms/availability/1/2023-09-01T10:00Z')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert f"Room 1" in data

    def test_get_overlapping_bookings(self):
        response = client.get('/api/rooms/overlap')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
