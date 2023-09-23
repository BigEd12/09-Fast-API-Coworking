from datetime import datetime

from utils.datetime.datetime import convert_time

def overlap(booking1, booking2):
    if booking1.id_room != booking2.id_room:
        return False
    else:
        date_format = "%Y-%m-%d %H:%M"
        start1 = booking1.start
        end1 = booking1.end
        start2 = booking2.start
        end2 = booking2.end
        start1_date_time = convert_time(start1)
        end1_date_time = convert_time(end1)
        start2_date_time = convert_time(start2)
        end2_date_time = convert_time(end2)
        return start1_date_time < end2_date_time and start2_date_time < end1_date_time

def check_overlap(bookings):
    overlapping_bookings = []

    for i, booking1 in enumerate(bookings):
        for j, booking2 in enumerate(bookings):
            if i != j and overlap(booking1, booking2):
                overlapping_bookings.append((booking1, booking2))
    
    if len(overlapping_bookings) == 0:
        return {'message': 'No overlapping bookings'}
    else:
        overlapping_list = []
        for booking_pair in overlapping_bookings:
            overlapping_dict = {
                'booking1': booking_pair[0],
                'booking2': booking_pair[1]
            }
            overlapping_list.append(overlapping_dict)
        
        return {f'{len(overlapping_list)} Overlapping bookings found':  overlapping_list}