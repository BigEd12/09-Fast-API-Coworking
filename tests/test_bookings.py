# from fastapi.testclient import TestClient

# from database.db import Session
# from database.models import Booking

# from main import app

# client = TestClient(app)

# def get_db_session():
#     db_session = Session()
#     try:
#         yield db_session
#     finally:
#         db_session.close()

# #----- GET /bookings -----#
# def test_bookings_response_code():
#     response = client.get('/api/bookings')
#     assert response.status_code == 200

# def test_booking_response_type():
#     response = client.get('/api/bookings')
#     response_data = response.json()
#     assert isinstance(response_data, dict)
    
# def test_booking_content():
#     with Session() as session:
#         response = client.get('/api/bookings')
#         response_data = response.json()
        
#         bookings = session.query(Booking).all()
#         if bookings:
#             assert len(response_data) != 0
#         else:
#             assert len(response_data) == 0
            
# #----- POST /bookings -----#
# def test_bookings_post_response_code():
#     response = client.post('/api/bookings')
#     assert response.status_code == 200


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestBookingEndpoints:
    def test_get_all_bookings(self):
        response = client.get('/api/bookings')
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert "All bookings" in response_data

    def test_make_new_booking(self):
        data = {
            "id_room": 1,
            "id_client": 1,
            "start": "2023-09-24T12:00Z",
            "end": "2023-09-24T14:00Z",
        }
        response = client.post('/api/bookings/make', data=data)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert "Booking confirmed" in response_data

    def test_get_bookings_by_filter(self):
        params = {
            "client_id": 1,
            "room_id": 1,
        }
        response = client.get('/api/bookings/filter', params=params)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
