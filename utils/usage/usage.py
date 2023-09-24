from datetime import datetime, timedelta

from fastapi import HTTPException

from database.models import Room, Booking
from database.db import Session

from utils.datetime.datetime import convert_time

def room_open_hours(session: Session):
    """
    Calculates how long each room is open in a day
    """
    rooms = session.query(Room).all()
    rooms_open_hours = {}
    for room in rooms:
        open_time = datetime.strptime(room.opening, "%H:%M")
        close_time = datetime.strptime(room.closing, "%H:%M")
        rooms_open_hours[room.room_id] = (close_time - open_time).total_seconds() / 3600
    return rooms_open_hours

def total_days_in_range(session: Session):
    """
    Calculates the number of days in the range of bookings
    """
    bookings = session.query(Booking).all()
    date_list = []
    for booking in bookings:
        date_list.append(convert_time(booking.start))
    unique_dates = set(date.date() for date in date_list)
    return len(unique_dates)

def total_bookings_per_room(session: Session):
    """
    Calculates total time each room was used
    """
    bookings = session.query(Booking).all()
    total_room_usage = {}
    for booking in bookings:
        room_id = booking.id_room
        start = convert_time(booking.start)
        end = convert_time(booking.end)
        booking_time = end - start

        if room_id not in total_room_usage:
            total_room_usage[room_id] = booking_time
        else:
            total_room_usage[room_id] += booking_time
    return total_room_usage

def total_open_hours_per_room(session: Session):
    """
    Calculates total time each room is open
    """
    open_hours = {}
    rooms_open_hours = room_open_hours(session)
    num_unique_dates = total_days_in_range(session)
    for key, value in rooms_open_hours.items():
        open_hours[key] = timedelta(hours=value * num_unique_dates)
    return open_hours

def calculate_percentage_per_room(session: Session):
    """
    Calculates time room was used against open as a percentage
    """
    bookings_per_room = total_bookings_per_room(session)
    open_hours_per_room = total_open_hours_per_room(session)
    percentage_dict = {}
    
    for room_id, timedelta1 in open_hours_per_room.items():
        if room_id in bookings_per_room:
            timedelta2 = bookings_per_room[room_id]
            if timedelta1.total_seconds() == 0:
                percentage = 0.0
            else:
                percentage = round((timedelta2.total_seconds() / timedelta1.total_seconds()) * 100, 0)
        else:
            percentage = 0.0
        
        percentage_dict[room_id] = f'{percentage}%'
    
    return percentage_dict