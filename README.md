# FASTApi - Coworking

This is a project designed to delve deeper into FASTApi and develop skills further.

The concept is a coworking space, with rooms available to book. The result is an api that allows coworking users to book undertake a multitude of actions, which are all detailed in the report.

## Dependencies
All necessary downloads in requirements.txt.


    pip install -r requirements.txt

- FASTApi(Version 0.103.1)
- SQLAlchemy(Version 2.02.21)
- Uvicorn(Version 0.23.2)

## Database
On first run, database ('coworking.db') will be created when accessing the endpoint, which loads initial data:

    /api/data/load

## Server
To start the development server, use the command:

    uvicorn main:app

## Testing
Basic testing has been implemented to confirm status codes and response types.

## Endpoints
View REPORT for information on Endpoints.
