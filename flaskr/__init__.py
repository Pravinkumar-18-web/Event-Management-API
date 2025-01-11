import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, db, Event, Attendee, Schedule
from auth.auth import AuthError, requires_auth
from datetime import datetime
from flask import Blueprint, jsonify, request, abort

"""
Function: create_app
Purpose: Creates and configures the Flask application, including database setup,
         CORS configuration, and error handling.
Parameters:
    - test_config: Optional configuration for testing purposes (default: None).
Returns: The configured Flask app instance.
Setup:
    - Initializes the Flask app.
    - Sets up the database connection, including the test configuration if provided.
    - Configures CORS to allow cross-origin requests from specified origins.
    - Applies middleware for setting CORS headers after every request.
"""

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    Root Route
    Path: /
    Method: GET
    Description: Returns a welcome message to the Event Management application.
                 Provides basic information for users accessing the app.
    Response: JSON object with success status and a welcome message.
    """
    @app.route('/')
    def welcome():
        try:
            return jsonify({
                "success": True,
                "message": "Welcome to the Event Management Application! Enjoy browsing Upcoming Events data."
            })
        except Exception as e:
            abort(500, str(e))

    """
    Get Events
    Path: /events
    Method: GET
    Description: Fetches a list of all events in the database.
    Response: JSON object containing a list of events.
    """
    @app.route('/events', methods=['GET'])
    @requires_auth('read:events')
    def get_events(payload):
        try:
            events = Event.query.all()
            data = [{'id': e.id, 'name': e.name, 'date': e.date.isoformat()} for e in events]
            return jsonify({"success": True, "events": data}), 200
        except Exception as e:
            abort(500, str(e))

    """
    Get Event Details
    Path: /events/<event_id>
    Method: GET
    Description: Fetches the details of a specific event by its ID.
    Response: JSON object containing the event details, attendees, and schedules.
    """
    @app.route('/events/<int:event_id>', methods=['GET'])
    @requires_auth('read:events')
    def get_event(payload, event_id):
        try:
            event = Event.query.get(event_id)
            if not event:
                abort(404, "Event not found")
            attendees = [{'id': a.id, 'name': a.name, 'email': a.email} for a in event.attendees]
            schedules = [{'id': s.id, 'title': s.title, 'start_time': s.start_time.isoformat(),
                          'end_time': s.end_time.isoformat()} for s in event.schedules]
            return jsonify({
                "success": True,
                "event": {
                    "id": event.id,
                    "name": event.name,
                    "description": event.description,
                    "date": event.date.isoformat(),
                    "attendees": attendees,
                    "schedules": schedules
                }
            }), 200
        except Exception as e:
            abort(500, str(e))

    """
    Create Event
    Path: /events
    Method: POST
    Description: Creates a new event in the database.
    Response: JSON object containing the newly created event's details.
    """
    @app.route('/events', methods=['POST'])
    @requires_auth('create:events')
    def create_event(payload):
        data = request.get_json()
        try:
            new_event = Event(
                name=data['name'],
                description=data.get('description', None),
                date=datetime.fromisoformat(data['date']),
                organizer_id=data['organizer_id']
            )
            new_event.insert()
            return jsonify({"success": True, "event": new_event.format()}), 201
        except Exception as e:
            abort(400, str(e))

    """
    Add Attendee
    Path: /events/<event_id>/attendees
    Method: POST
    Description: Adds an attendee to a specific event by event ID.
    Response: JSON object containing the newly added attendee's details.
    """
    # @app.route('/events/<int:event_id>/attendees', methods=['POST'])
    # @requires_auth('manage:attendees')
    # def add_attendee(payload, event_id):
    #     data = request.get_json()
    #     try:
    #         event = Event.query.get(event_id)
    #         if not event:
    #             # abort(404, "Event not found")
    #             abort(404, description="Event not found")

    #         new_attendee = Attendee(name=data['name'], email=data['email'])
    #         new_attendee.insert()
    #         event.attendees.append(new_attendee)
    #         db.session.commit()

    #         return jsonify({"success": True, "attendee": new_attendee.format()}), 201
    #     except Exception as e:
    #         abort(400, str(e))

    @app.route('/events/<int:event_id>/attendees', methods=['POST'])
    @requires_auth('manage:attendees')
    def add_attendee(payload, event_id):
        
        data = request.get_json()

        # Fetch the event
        event = Event.query.get(event_id)
        if not event:
         # Raise 404 if the event is not found
            abort(404, description="Event not found")
        try:
            # Create a new attendee
            new_attendee = Attendee(name=data['name'], email=data['email'])
            new_attendee.insert()
            # Return success response
            return jsonify({"success": True, "attendee": new_attendee.format()}), 201

        except KeyError as e:
            # Handle missing keys in request payload
            abort(400, description=f"Missing key: {str(e)}")
        except Exception as e:
            # Handle all other exceptions
            abort(500, description=f"An unexpected error occurred: {str(e)}")

    """
    Add Schedule
    Path: /events/<event_id>/schedule
    Method: POST
    Description: Adds a schedule to a specific event by event ID.
    Response: JSON object containing the newly added schedule's details.
    """
    @app.route('/events/<int:event_id>/schedule', methods=['POST'])
    @requires_auth('create:schedule')
    def add_schedule(payload, event_id):
        data = request.get_json()
        
        event = Event.query.get(event_id)
        if not event:
            abort(404, "Event not found")
        try:
            new_schedule = Schedule(
                title=data['title'],
                start_time=datetime.fromisoformat(data['start_time']),
                end_time=datetime.fromisoformat(data['end_time']),
                event_id=event_id
            )
            new_schedule.insert()

            return jsonify({"success": True, "schedule": new_schedule.format()}), 201
        except Exception as e:
            abort(400, str(e))

    """
    Update Event
    Path: /events/<event_id>
    Method: PATCH
    Description: Updates the details of a specific event by event ID.
    Response: JSON object containing the updated event's details.
    """
    @app.route('/events/<int:event_id>', methods=['PATCH'])
    @requires_auth('update:events')
    def update_event(payload, event_id):
        data = request.get_json()
        event = Event.query.get(event_id)
        if not event:
            abort(404, "Event not found")
        try:
            if 'name' in data:
                event.name = data['name']
            if 'description' in data:
                event.description = data['description']
            if 'date' in data:
                event.date = datetime.fromisoformat(data['date'])

            event.update()
            return jsonify({"success": True, "event": event.format()}), 200
        except Exception as e:
            abort(400, str(e))

    """
    Delete Event
    Path: /events/<event_id>
    Method: DELETE
    Description: Deletes a specific event by event ID.
    Response: JSON object confirming the deletion of the event.
    """
    @app.route('/events/<int:event_id>', methods=['DELETE'])
    @requires_auth('delete:events')
    def delete_event(payload, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, "Event not found")
        try:
            event.delete()
            return jsonify({"success": True, "deleted": event_id}), 200
        except Exception as e:
            abort(400, str(e))

    """
    Error Handlers
    400 - Bad Request: Triggered when the request is invalid or missing required data.
    Response: JSON object with an error code (400) and a description of the issue.

    404 - Not Found: Triggered when a resource (Event, Schedule, or Attendees) is not found in the database.
    Response: JSON object with an error code (404) and a description of the issue.

    500 - Internal Server Error: Triggered for unexpected errors in the application.
    Response: JSON object with an error code (500) and a message describing the issue.

    AuthError: Triggered when there is an authentication or authorization failure.
    Response: JSON object with the relevant error code and description.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": str(error.description)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": str(error.description)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "An unexpected error occurred: " + str(error.description)
        }), 500

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error['description']
        }), error.status_code

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
