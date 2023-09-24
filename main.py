from datetime import datetime
from fastapi import FastAPI, Depends, Form, Query
from starlette.responses import RedirectResponse
from typing import Optional

from database.models import Room, Client, Booking
from database.db import Session

from routers import client_routes, booking_routes, room_routes

from original_data.original_data import data

from utils.datetime.datetime import convert_time
from utils.overlap.overlap import check_overlap
from utils.usage.usage import calculate_percentage_per_room

app = FastAPI()

def get_db_session():
    db_session = Session()
    try:
        yield db_session
    finally:
        db_session.close()

#----- INDEX / DOCS ENDPOINT -----#
@app.get('/')
def index():
    return RedirectResponse(url='/docs')


#----- INITIAL DATA ENDPOINT -----#

@app.post('/data/load')
def load_initial_data(session: Session = Depends(get_db_session)):
    """
    Populates database with initial load data if empty
    """
    try:
        if (
            session.query(Room).count() == 0 and
            session.query(Client).count() == 0 and
            session.query(Booking).count() == 0
        ):
            for room_data in data.get("rooms", []):
                room_data["room_id"] = room_data.pop("id")
                room_data["opening"] = room_data["opening"]
                room_data["closing"] = room_data["closing"]
                room = Room(**room_data)
                session.add(room)

            for client_data in data.get("clients", []):
                client_data["client_id"] = client_data.pop("id")
                client = Client(**client_data)
                session.add(client)

            for booking_data in data.get("bookings", []):
                booking = Booking(**booking_data)
                session.add(booking)

            session.commit()
            return {"message": "Data added to the database successfully."}
        else:
            return {'message': 'Database is already populated.'}
    except Exception as e:
        return {"error": str(e)}

#----- BOOKING ENDPOINTS -----#
app.include_router(booking_routes.router, prefix="/api/bookings")

# #----- ROOM ENDPOINTS -----#
app.include_router(room_routes.router, prefix="/api/rooms")
    
# #----- CLIENT ENDPOINT -----#
app.include_router(client_routes.router, prefix="/api/clients")
