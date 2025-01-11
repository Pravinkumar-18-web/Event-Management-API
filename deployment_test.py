import os
import unittest
import json

import requests


class CapstoneTestCase(unittest.TestCase):

    def setUp(self):
        self.api = "https://fsnd-capstone-a261584c79ff.herokuapp.com"

        self.movie = {
            "title": "Valimai",
            "release_date": "09-01-2025"
        }

        self.actor = {
            "name": "Ajith",
            "age": 45,
            "gender": 'M',
            "movie_id": 2
        }

        # Set up authentication tokens info
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())

        assistant_jwt = self.auth["roles"]["Casting Assistant"]["jwt_token"]
        director_jwt = self.auth["roles"]["Casting Director"]["jwt_token"]
        producer_jwt = self.auth["roles"]["Executive Producer"]["jwt_token"]
        self.auth_headers = {
            "Casting Assistant": f'Bearer {assistant_jwt}',
            "Casting Director": f'Bearer {director_jwt}',
            "Executive Producer": f'Bearer {producer_jwt}'
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

# Test: Get Movies (Successful)
# Validates that the `/movies` endpoint returns a list of movies for a Casting Assistant role.
    def test_get_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = requests.get(self.api + '/movies', headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["movies"]), type([]))

# Test: Get Actors (Successful)
# Verifies that the `/actors` endpoint returns a list of actors for a Casting Assistant role.
    def test_get_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = requests.get(self.api + '/actors', headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

# Test: Get Actors (Successful)
# Verifies that the `/actors` endpoint returns a list of actors for a Casting Assistant role.
    def test_get_actors_by_director(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = requests.get(self.api + '/actors', headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(type(data["actors"]), type([]))

# Test: Get Actors (Unauthorized)
# Confirms that accessing the `/actors` endpoint without authorization results in a 401 error.
    def test_get_actor_fail_401(self):
        res = requests.get(self.api + '/actors')
        data = res.json()

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data['success'])
        self.assertEqual(type(data["message"]), type(""))

# Test: Create Movie (Bad Request)
# Validates that creating a movie with missing fields returns a 400 error for the Executive Producer role.
    def test_create_movies_fail_400(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        movie_fail = {"title": "Movie"}
        res = requests.post(
            self.api + f'/movies',
            json=movie_fail,
            headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Movie")

# Test: Create Movie (Forbidden)
# Ensures that a Casting Director cannot create a movie, resulting in a 403 error.
    def test_create_movies_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        movie_fail = {"title": "Movie"}
        res = requests.post(
            self.api + f'/movies',
            json=movie_fail,
            headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])

# Test: Create Actor (Bad Request)
# Validates that creating an actor with missing fields returns a 400 error for the Casting Director role.
    def test_create_actors_fail_400(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        actor_fail = {"name": "Actor"}
        res = requests.post(
            self.api + f'/actors',
            json=actor_fail,
            headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "Missing field for Actor")

# Test: Create Actor (Forbidden)
# Confirms that a Casting Assistant cannot create an actor, resulting in a 403 error.
    def test_create_actors_fail_403(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        actor_fail = {"name": "Actor"}
        res = requests.post(
            self.api + f'/actors',
            json=actor_fail,
            headers=header_obj)
        data = res.json()

        self.assertEqual(res.status_code, 403)
        self.assertFalse(data['success'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
