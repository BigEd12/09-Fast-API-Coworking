from fastapi import FastAPI
from starlette.responses import RedirectResponse

from database.db import Session

from routers import client_routes, booking_routes, room_routes, data_routes

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
    """
    Redirects to Docs
    """
    return RedirectResponse(url='/docs')


#----- INITIAL DATA ENDPOINT -----#
app.include_router(data_routes.router, prefix="/api/data")

#----- BOOKING ENDPOINTS -----#
app.include_router(booking_routes.router, prefix="/api/bookings")

# #----- ROOM ENDPOINTS -----#
app.include_router(room_routes.router, prefix="/api/rooms")
    
# #----- CLIENT ENDPOINT -----#
app.include_router(client_routes.router, prefix="/api/clients")
