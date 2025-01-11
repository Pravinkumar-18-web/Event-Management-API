# Event-Management-API
Udacity Full-Stack Web Developer Nanodegree Program Capstone Project

## Project Description
A Flask-based RESTful API for organizing and managing events. Users can create, join, and manage events while assigning roles like Organizer, Attendee, and Admin. The API includes endpoints to manage event details, attendees, and schedules.

### Key Dependencies & Platforms

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

- [Auth0](https://auth0.com/docs/) is the authentication and authorization system we'll use to handle users with different roles with more secure and easy ways

- [PostgreSQL](https://www.postgresql.org/) this project is integrated with a popular relational database PostgreSQL, though other relational databases can be used with a little effort.

- [Heroku](https://www.heroku.com/what) is the cloud platform used for deployment


### Running Locally

#### Installing Dependencies

##### Python 3.9

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

##### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Once you have your virtual environment setup and running, install dependencies by running:

```cmd
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Database Setup
With Postgres running, restore a database using the `setup.psql` file provided. In terminal run:

```cmd
createdb event_management
psql event_management < setup.psql
```

#### Running Tests
To execute local run using `test_app.py` and before that set the local database URl 
```cmd
dropdb event_management_test
createdb event_management_test
psql event_management_test < setup.psql
python test_app.py
```
To execute test for live application using `deployment_test.py` and before that set database URl which you have config for Heroku.
```cmd
dropdb event_management_test
createdb event_management_test
psql event_management_test < setup.psql
python deployment_test.py
```

#### Auth0 Setup

You need to setup an Auth0 account.

Environment variables needed: (env_file.bat)

```cmd
set AUTH0_DOMAIN="xxxxxxxxxx.auth0.com" # Choose your tenant domain
set ALGORITHMS="RS256"
set API_AUDIENCE="xxxxxxxxx" # Create an API in Auth0
```

##### Roles

Create three roles for users under `Users & Roles` section in Auth0

* Attendees:
	* Can view events and schedules details/
* Organizer:
	* All permissions a Attendees has and…
	* Create Schedules for an events from the database
	* Add attendees for an events from the database
* Executive Producer
	* All permissions a Organizer has and…
	* Add or update or delete an events from the database

##### Permissions

Following permissions should be created under created API settings.

* `read:events`
* `create:events`
* `create:schedule`
* `manage:attendees`
* `delete:events`
* `update:events`

##### Set JWT Tokens in `auth_config.json`

Use the following link to create users and sign them in. This way, you can generate 

```
https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
```

#### Launching The App

1. Initialize and activate a virtualenv:

   ```cmd
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install the dependencies:

    ```cmd
    pip install -r requirements.txt
    ```
3. Configure database path to connect local postgres database in `models.py`

    ```python
    database_path = "postgres://{}/{}".format('localhost:5432', 'event_management')
    ```
**Note:** For default postgres installation, default user name is `postgres` with no password. Thus, no need to speficify them in database path. You can also omit host and post (localhost:5432). But if you need, you can use this template:

```
postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
```
For more details [look at the documentation (31.1.1.2. Connection URIs)](https://www.postgresql.org/docs/9.3/libpq-connect.html)

4. Setup the environment variables for Auth0 under `env_file.bat` running:

	```cmd
	env_file.bat
	```
	
5.  To run the server locally, execute:

    ```cmd
    export FLASK_APP=flaskr
    export FLASK_DEBUG=True
    export FLASK_ENVIRONMENT=debug
    flask run --reload
    ```

## API Documentation

### Models

* Event
   * id (Primary Key, Integer)
   * name (String, unique, nullable=False)
   * description (Text)
   * date (DateTime)
   * organizer_id (Foreign Key, Integer)
* Attendee
   * id (Primary Key, Integer)
   * name (String, nullable=False)
   * email (String, unique, nullable=False)
   * Many-to-many relationship with Event
* Schedule
   * id (Primary Key, Integer)
   * title (String, nullable=False)
   * start_time (DateTime)
   * end_time (DateTime)
   * event_id (Foreign Key, Integer)


### Error Handling

Errors are returned as JSON objects in the following format:

```json
{
    "success": false, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource Not Found
- 500: Internal Server Error

### Endpoints

#### GET /events
* Returns a list of all events.
* Requires `read:events` permission.

* **Example Request:** `curl 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events'`

* **Expected Result:**
    ```json
    {
        "events": [
            {
                "date": "2025-03-15T09:00:00",
                "id": 1,
                "name": "Tech Conference"
            },
            {
                "date": "2025-04-20T10:00:00",
                "id": 2,
                "name": "Art Expo"
            },
            {
                "date": "2025-03-15T09:00:00",
                "id": 3,
                "name": "Technology expo"
            }
        ],
        "success": true
    }
    ```
	
#### GET /events/<event_id>:

* Returns details of a specific event, including its attendees and schedule.

* Requires `read:events` permission.

* **Example Request:** `curl 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/1'`

* **Expected Result:**
    ```json
	{
    "event": {
        "attendees": [
            {
                "email": "alice@example.com",
                "id": 1,
                "name": "Alice Johnson"
            },
            {
                "email": "bob@example.com",
                "id": 2,
                "name": "Bob Smith"
            }
        ],
        "date": "2025-03-15T09:00:00",
        "description": "Annual tech conference on innovation.",
        "id": 1,
        "name": "Tech Conference",
        "schedules": [
            {
                "end_time": "2025-03-15T10:30:00",
                "id": 1,
                "start_time": "2025-03-15T09:30:00",
                "title": "Keynote Speech"
            },
            {
                "end_time": "2025-03-15T12:30:00",
                "id": 2,
                "start_time": "2025-03-15T11:00:00",
                "title": "Workshop on AI"
            },
            {
                "end_time": "2025-03-15T21:30:00",
                "id": 3,
                "start_time": "2025-03-15T21:00:00",
                "title": "Cameo speech"
            }
        ]
    },
    "success": true
    }
	```
	
#### POST /events

* Creates a new event.

* Requires `create:events` permission.

* **Example Request:** (Create)
    ```cmd
	curl --location --request POST 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events' \
		--header 'Content-Type: application/json' \
		--data-raw '{"date": "2025-03-15T09:00:00",
        "description": "conference on technology",
        "organizer_id":3,
        "name": "Technology expo"}'
    ```
    
* **Example Response:**
    ```json
	{
    "event": {
        "attendees": [],
        "date": "Sat, 15 Mar 2025 09:00:00 GMT",
        "description": "conference on technology",
        "id": 3,
        "name": "Technology expo",
        "organizer_id": 3,
        "schedules": []
    },
    "success": true
    }
    ```

#### POST /events/<event_id>/attendees

* Adds an attendee to the event.

* Requires manage:attendees permission.

* **Example Request:** (Create)
    ```bash
	curl --location --request POST 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/1/attendees' \
		--header 'Content-Type: application/json' \
		--data-raw '{
        "email": "Ravin@example.com",
        "name": "Ravinkumar J"
        }'
    ```
    
* **Example Response:**
    ```json
	{
    "attendee": {
        "email": "Ravin@example.com",
        "id": 3,
        "name": "Ravinkumar J"
    },
    "success": true
    }
    ```

#### POST /events/<event_id>/schedule

* Adds a schedule entry to the event.

* Requires `create:schedule` permission.

* **Example Request:** (Create)
    ```bash
	curl --location --request POST 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/1/schedule' \
		--header 'Content-Type: application/json' \
		--data-raw '{
        "end_time": "2025-03-15T21:30:00",
        "start_time": "2025-03-15T21:00:00",
        "title": "Cameo speech"
        }'
    ```
    
* **Example Response:**
    ```json
    {
    "schedule": {
            "end_time": "Sat, 15 Mar 2025 21:30:00 GMT",
            "event_id": 1,
            "id": 3,
            "start_time": "Sat, 15 Mar 2025 21:00:00 GMT",
            "title": "Cameo speech"
        },
        "success": true
    }
    ```

#### PATCH /events/<event_id>

* Updates event details (e.g., name, description, or date).

* Requires `update:events` permission.

* **Example Request:** 

    ```bash
	curl --location --request PATCH 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/2' \
		--header 'Content-Type: application/json' \
		--data-raw '{"date": "2025-03-15T09:00:00",
        "description": "Graduation conference on techno",
        "organizer_id":3,
        "name": "Graduation day "}'
    ```

* **Example Response:**
    ```json
	{
    "event": {
        "attendees": [],
        "date": "Sat, 15 Mar 2025 09:00:00 GMT",
        "description": "Graduation conference on techno",
        "id": 2,
        "name": "Graduation day ",
        "organizer_id": 2,
        "schedules": []
    },
    "success": true
    }   
    ```

#### DELETE /events/<event_id>

* Deletes an event and all associated data.

* Requires `delete:events` permission.

* **Example Request:** `curl --request DELETE 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/4'`

* **Example Response:**
    ```json
	{
    "deleted": 3,
    "success": true
    }   
    ```
    
#### Live Application URL :

```bash
https://eventmanagementapi-1950dbc6e726.herokuapp.com/
``` 