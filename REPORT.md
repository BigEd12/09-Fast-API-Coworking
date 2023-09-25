## Description of Implementation

This FastAPI project aims to provide a RESTful API for managing and querying coworking space-related data, including information about rooms, clients, bookings, and usage statistics. The implementation is designed to be intuitive and user-friendly, catering to the needs of a coworking space management system.

I have chosen FastAPI as the framework for its ease of use, speed, and compatibility with SQLAlchemy for database interactions. The API provides a wide range of functionality, from listing available bookings and creating new bookings to obtaining room usage percentages and checking room availability at specific timestamps.

## API Routes

1. **Load Initial Data**

   - **Description:** This endpoint checks if the database is empty and, if so, populates it with initial data.

   - **Route:** `/api/data/load`

1. **List of All Bookings**

   - **Description:** This endpoint retrieves and returns all available booking records from the database.

   - **Route:** `/api/bookings`

2. **Create a New Booking**

   - **Description:** This endpoint allows you to create a new booking with the specified room, client, and time slot.

   - **Route:** `/api/bookings/make`

3. **Filter Bookings**

   - **Description:** This endpoint retrieves and returns booking records based on optional filters, including filtering by client ID and room ID.

   - **Route:** `/api/bookings/filter`

4. **List of Bookings by All Clients**

   - **Description:** This endpoint retrieves and returns all bookings made by each client in the database.

   - **Route:** `/api/clients/bookings`

5. **List of All Rooms**

   - **Description:** This endpoint allows you to retrieve information about all rooms in the database.

   - **Route:** `/api/rooms/all`

6. **Add a New Room**

   - **Description:** This endpoint allows you to add a new room with specified opening and closing times and a designated capacity to the database.

   - **Route:** `/api/rooms/add`

7. **Room Usage Percentage**

   - **Description:** This endpoint calculates and returns the percentage of time each room has been used in the time available based on bookings in the database.

   - **Route:** `/api/rooms/usage`

8. **Check Room Availability**

   - **Description:** This endpoint allows you to check the availability of a specific room at a given timestamp.

   - **Route:** `/api/rooms/availability/{room_id}/{timestamp}`

9. **List of Overlapping Bookings**

   - **Description:** This endpoint retrieves all overlapping booking pairs from the database.

   - **Route:** `/api/rooms/overlap`

## Additional Features

- **Testing Implementation**: Despite not being a specific requirement, basic testing has been implemented for the API using FastAPI's TestClient.

## Limitations and Improvements

- The current implementation assumes that bookings are non-recurring and do not span multiple days. Support for recurring bookings could be added.
- Handling booking requests based on room availability is a feature that could be implemented.

This report provides a high-level overview of the implemented API and its features. Detailed documentation for each endpoint, including input parameters and examples, is available within the codebase's docstrings.
