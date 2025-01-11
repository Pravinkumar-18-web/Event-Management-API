# Event Management API  
**Udacity Full-Stack Web Developer Nanodegree Program Capstone Project**

## Project Description  
A Flask-based RESTful API for organizing and managing events. Users can create, join, and manage events while assigning roles such as Organizer, Attendee, and Admin. The API includes endpoints for managing event details, attendees, and schedules.

### Key Dependencies & Platforms  

- **[Flask](http://flask.pocoo.org/)**: A lightweight backend microservices framework that handles requests and responses.  
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: The Python SQL toolkit and ORM for interacting with the SQLite database. You'll primarily work in `app.py` and can reference `models.py`.  
- **[Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#)**: An extension to handle cross-origin requests from the frontend server.  
- **[Auth0](https://auth0.com/docs/)**: A system used for authentication and authorization, enabling secure user management with various roles.  
- **[PostgreSQL](https://www.postgresql.org/)**: A popular relational database integrated into this project, though other relational databases can be used with minimal changes.  
- **[Heroku](https://www.heroku.com/what)**: The cloud platform used for deployment.  

### Running Locally  

#### Installing Dependencies  

##### Python 3.9  
To install the latest version of Python for your platform, follow the instructions in the [Python documentation](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).

##### Virtual Environment  
We recommend using a virtual environment for managing project dependencies separately. Instructions for setting up a virtual environment can be found in the [Python packaging documentation](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

Once your virtual environment is set up, install the required dependencies by running:

```cmd
pip install -r requirements.txt
```

#### Database Setup  
With PostgreSQL running, restore the database using the provided `setup.psql` file. Run the following commands in the terminal:

```cmd
createdb event_management
psql event_management < setup.psql
```

#### Running Tests  
Before running the tests, set the environment variable for the database URL and update the JWT tokens in the `auth_config.json` file.

For local testing, set the local database URL and run the following commands:

```cmd
dropdb event_management_test
createdb event_management_test
psql event_management_test < setup.psql
python test_app.py
```

For testing the live application, set the database URL configured for Heroku:

```cmd
dropdb event_management_test
createdb event_management_test
psql event_management_test < setup.psql
python deployment_test.py
```

#### Auth0 Setup  

To use Auth0 for authentication, create an Auth0 account and configure the following environment variables in `env_file.bat`:

```cmd
set AUTH0_DOMAIN="xxxxxxxxxx.auth0.com" # Choose your tenant domain
set ALGORITHMS="RS256"
set API_AUDIENCE="xxxxxxxxx" # Create an API in Auth0
```

##### Roles  
Create three user roles under the **Users & Roles** section in Auth0:

- **Attendees**: Can view events and schedule details.
- **Organizer**: Has the same permissions as Attendees, with additional permissions to create schedules and add attendees.
- **Executive Producer**: Has the same permissions as Organizer, with additional permissions to add, update, or delete events.

##### Permissions  
Create the following permissions under your created API settings:

- `read:events`
- `create:events`
- `create:schedule`
- `manage:attendees`
- `delete:events`
- `update:events`

##### Set JWT Tokens in `auth_config.json`  
Use the link below to create users and sign them in, generating the appropriate JWT tokens:

```
https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
```

### Launching the App  

1. **Initialize and activate a virtual environment**:

    ```cmd
    python -m venv venv
    .\venv\Scripts\activate
    ```

2. **Install dependencies**:

    ```cmd
    pip install -r requirements.txt
    ```

3. **Configure the database path to connect to your local PostgreSQL database in `models.py`**:

    ```python
    database_path = "postgres://{}/{}".format('localhost:5432', 'event_management')
    ```

    **Note**: For a default PostgreSQL installation, the default username is `postgres` with no password. You can omit the username, password, host, and port. However, if needed, you can use the following template:

    ```
    postgresql://[user[:password]@][netloc][:port][/dbname][?param1=value1&...]
    ```

    For more details, refer to the [documentation (31.1.1.2. Connection URIs)](https://www.postgresql.org/docs/9.3/libpq-connect.html).

4. **Set the environment variables for Auth0** by running:

    ```cmd
    env_file.bat
    ```

5. **Run the server locally** by executing the following:

    ```cmd
    export FLASK_APP=flaskr
    export FLASK_DEBUG=True
    export FLASK_ENVIRONMENT=debug
    flask run --reload
    ```

## API Documentation  

### Models  

- **Event**  
   - `id` (Primary Key, Integer)  
   - `name` (String, unique, nullable=False)  
   - `description` (Text)  
   - `date` (DateTime)  
   - `organizer_id` (Foreign Key, Integer)

- **Attendee**  
   - `id` (Primary Key, Integer)  
   - `name` (String, nullable=False)  
   - `email` (String, unique, nullable=False)  
   - Many-to-many relationship with Event  

- **Schedule**  
   - `id` (Primary Key, Integer)  
   - `title` (String, nullable=False)  
   - `start_time` (DateTime)  
   - `end_time` (DateTime)  
   - `event_id` (Foreign Key, Integer)  

### Error Handling  
Errors are returned as JSON objects in the following format:

```json
{
    "success": false,
    "error": 400,
    "message": "bad request"
}
```

The API will return the following error types when requests fail:

- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Resource Not Found
- `500`: Internal Server Error

### Endpoints  

#### `GET /events`  
Returns a list of all events. Requires `read:events` permission.  

**Example Request:**  
```bash
curl 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events'
```

**Expected Response:**  

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

#### `GET /events/<event_id>`  
Returns details of a specific event, including its attendees and schedule. Requires `read:events` permission.

**Example Request:**  
```bash
curl 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events/1'
```

**Expected Response:**  

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

#### `POST /events`  
Creates a new event. Requires `create:events` permission.

**Example Request:**  

```bash
curl --location --request POST 'https://eventmanagementapi-1950dbc6e726.herokuapp.com/events' \
    --header 'Content-Type: application/json' \
    --data-raw '{"date": "2025-03-15T09:00:00", "description": "conference on technology", "organizer_id": 3, "name": "Technology expo"}'
```

**Example Response:**  

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

#### Live Application URL:

```bash
https://eventmanagementapi-1950dbc6e726.herokuapp.com/
```