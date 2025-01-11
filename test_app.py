import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import db, Event, Attendee, Schedule

class EventManagementTestCase(unittest.TestCase):
    def setUp(self):
        """Executed before each test."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ.get('DATABASE_URL_Test', "postgresql://postgres:1898@localhost:5432/event_management_test")

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })

        # Test data
        self.event_data = {
            "name": "Tech Conference",
            "date": "2025-03-15T09:00:00",
            "organizer_id": 1
        }
        self.event_data_1 = {
            "name": "MS hackthon",
            "date": "2025-03-25T20:20:00",
            "organizer_id": 2
        }

        self.attendee_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        self.attendee_data_1 = {
            "name": "pk12",
            "email": "pravin23@example.com"
        }

        self.schedule_data = {
            "title": "Keynote Speech",
            "start_time": "2025-03-15T09:30:00",
            "end_time": "2025-03-15T10:30:00"
        }

        # Set up authentication tokens info (this is assumed to be set up in 'auth_config.json')
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())

        self.auth_headers = {
            "Attendee": f'Bearer {self.auth["roles"]["Attendee"]["jwt_token"]}',
            "Organizer": f'Bearer {self.auth["roles"]["Organizer"]["jwt_token"]}',
            "Admin": f'Bearer {self.auth["roles"]["Admin"]["jwt_token"]}'
        }

        # Bind the app context
        with self.app.app_context():
            db.create_all()

    # def tearDown(self):
    #     """Executed after each test."""
    #     pass
    def tearDown(self):
        """Executed after each test to clean up test data."""
        with self.app.app_context():
            db.session.query(Attendee).delete()
            db.session.query(Schedule).delete()
            db.session.query(Event).delete()
            db.session.commit()
    # TEST CASES

    # Success behavior tests

    def test_get_events_success(self):
        # First, create an event
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)
        
        
        header_obj = {
            "Authorization": self.auth_headers["Attendee"]
        }
        res = self.client().get('/events', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['events']) > 0)

    def test_create_event_success(self):
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        event_data = {
            "name": "TEK Conference",
            "date": "2025-03-15T03:40:00",
            "organizer_id": 3
        }
        res = self.client().post('/events', json=event_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['event']['name'], event_data["name"])

    def test_add_attendee_success(self):
        # First, create an event
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)
        
        event_id = data['event']['id']
        

        # Add an attendee
        header_obj = {
            "Authorization": self.auth_headers["Organizer"]
        }
       
        res = self.client().post(f'/events/{event_id}/attendees', json=self.attendee_data, headers=header_obj)
        data = json.loads(res.data)
        

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['attendee']['name'], self.attendee_data["name"])

    def test_add_schedule_success(self):
        # First, create an event
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)
        
        event_id = data['event']['id']

        # Add a schedule
        header_obj = {
            "Authorization": self.auth_headers["Organizer"]
        }
        res = self.client().post(f'/events/{event_id}/schedule', json=self.schedule_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['schedule']['title'], self.schedule_data["title"])

    # Error behavior tests

    def test_get_events_fail_401(self):
        res = self.client().get('/events')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), type(""))

    def test_create_event_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Attendee"]
        }
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Permission not found.")

    def test_add_attendee_fail_404(self):
        event_id = 999  # Non-existing event
        header_obj = {
            "Authorization": self.auth_headers["Organizer"]
        }
        res = self.client().post(f'/events/{event_id}/attendees', json=self.attendee_data, headers=header_obj)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['message'], 'Event not found')

    
    def test_add_schedule_fail_404(self):
        event_id = 999  # Non-existing event
        header_obj = {
            "Authorization": self.auth_headers["Organizer"]
        }
        res = self.client().post(f'/events/{event_id}/schedule', json=self.schedule_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    # RBAC tests

    def test_admin_create_event(self):
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        self.event_data = {
            "name": "MultiInter Conference",
            "date": "2025-03-15T03:00:00",
            "organizer_id": 2
        }
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['success'])

    def test_admin_delete_event(self):
        # Create an event
        header_obj = {
            "Authorization": self.auth_headers["Admin"]
        }
        res = self.client().post('/events', json=self.event_data_1, headers=header_obj)
        data = json.loads(res.data)
        event_id = data['event']['id']

        # Delete the event
        res = self.client().delete(f'/events/{event_id}', headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_organizer_create_event_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Organizer"]
        }
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

    def test_attendee_create_event_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Attendee"]
        }
        res = self.client().post('/events', json=self.event_data, headers=header_obj)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
