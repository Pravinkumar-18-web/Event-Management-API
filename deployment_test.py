import unittest
import json
import requests

class EventManagementTestCase(unittest.TestCase):
    def setUp(self):
        """Executed before each test."""
        self.api_url = "https://eventmanagementapi-1950dbc6e726.herokuapp.com"

        # Test data
        self.event_data = {
            "name": "Tech Conference",
            "date": "2025-03-15T09:00:00",
            "organizer_id": 1
        }
        self.attendee_data = {
            "name": "John Durai",
            "email": "johnDuraj@example.com"
        }

        self.schedule_data = {
            "title": "Keynote Speech",
            "start_time": "2025-03-15T09:30:00",
            "end_time": "2025-03-15T10:30:00"
        }

        # Authentication tokens info (assumed to be set up in 'auth_config.json')
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())

        self.auth_headers = {
            "Attendee": {"Authorization": f'Bearer {self.auth["roles"]["Attendee"]["jwt_token"]}'},
            "Organizer": {"Authorization": f'Bearer {self.auth["roles"]["Organizer"]["jwt_token"]}'},
            "Admin": {"Authorization": f'Bearer {self.auth["roles"]["Admin"]["jwt_token"]}'}
        }

    def test_get_events_success(self):
        """Test fetching events successfully."""
        response = requests.get(f"{self.api_url}/events", headers=self.auth_headers["Attendee"])
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['events']) > 0)

    def test_create_event_success(self):
        """Test creating an event successfully."""
        event_data = {
            "name": "AI ON HUMANS",
            "date": "2025-03-13T20:20:00",
            "organizer_id": 3
        }
        response = requests.post(f"{self.api_url}/events", json=event_data, headers=self.auth_headers["Admin"])
        data = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['event']['name'], event_data["name"])

    def test_add_attendee_success(self):
        """Test adding an attendee to an event successfully."""
        # Create an event
        Event_data = {
            "name": "cold werd discussion",
            "date": "2025-03-05T09:00:00",
            "organizer_id": 2
        }
        event_response = requests.post(f"{self.api_url}/events", json=Event_data, headers=self.auth_headers["Admin"])
        event_data = event_response.json()
        event_id = event_data['event']['id']

        # Add an attendee
        response = requests.post(f"{self.api_url}/events/{event_id}/attendees", json=self.attendee_data, headers=self.auth_headers["Organizer"])
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['attendee']['name'], self.attendee_data["name"])

    def test_add_schedule_success(self):
        """Test adding a schedule to an event successfully."""
        # Create an event
        event_data = {
            "name": "spaceX conference",
            "date": "2025-03-15T09:00:00",
            "organizer_id": 1
        }
        event_response = requests.post(f"{self.api_url}/events", json=event_data, headers=self.auth_headers["Admin"])
        event_data = event_response.json()
        event_id = event_data['event']['id']


        # Add a schedule
        response = requests.post(f"{self.api_url}/events/{event_id}/schedule", json=self.schedule_data, headers=self.auth_headers["Organizer"])
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['schedule']['title'], self.schedule_data["title"])

    def test_get_events_fail_401(self):
        """Test unauthorized access to get events."""
        response = requests.get(f"{self.api_url}/events")
        data = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), str)

    def test_create_event_fail_403(self):
        """Test forbidden access when attendee tries to create an event."""
        response = requests.post(f"{self.api_url}/events", json=self.event_data, headers=self.auth_headers["Attendee"])
        data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Permission not found.")

    def test_add_attendee_fail_404(self):
        """Test adding an attendee to a non-existing event."""
        event_id = 999  # Non-existing event
        response = requests.post(f"{self.api_url}/events/{event_id}/attendees", json=self.attendee_data, headers=self.auth_headers["Organizer"])
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Event not found")

    def test_add_schedule_fail_404(self):
        """Test adding a schedule to a non-existing event."""
        event_id = 999  # Non-existing event
        response = requests.post(f"{self.api_url}/events/{event_id}/schedule", json=self.schedule_data, headers=self.auth_headers["Organizer"])
        data = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])

    def test_admin_delete_event(self):
        """Test admin deleting an event successfully."""
        # Create an event
        event_data_1 = {
            "name": "MS Hackathon",
            "date": "2025-03-25T20:20:00",
            "organizer_id": 2
        }
        event_response = requests.post(f"{self.api_url}/events", json=event_data_1, headers=self.auth_headers["Admin"])
        event_data = event_response.json()
        event_id = event_data['event']['id']

        # Delete the event
        response = requests.delete(f"{self.api_url}/events/{event_id}", headers=self.auth_headers["Admin"])
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])

    def test_organizer_create_event_fail_403(self):
        """Test organizer attempting to create an event (forbidden)."""
        response = requests.post(f"{self.api_url}/events", json=self.event_data, headers=self.auth_headers["Organizer"])
        data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])

    def test_attendee_create_event_fail_403(self):
        """Test attendee attempting to create an event (forbidden)."""
        response = requests.post(f"{self.api_url}/events", json=self.event_data, headers=self.auth_headers["Attendee"])
        data = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
