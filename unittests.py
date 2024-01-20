import unittest
from unittest.mock import patch
from flask import Flask
from flask_testing import TestCase
from main import app, LiveList, LiveInPlaying, LiveMatch, UpcomingMatches, TopFiveLeagues

class TestApp(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_live_list(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'test_key': 'test_value'}
            response = self.client.get('/api/football/live/list')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'test_key': 'test_value'})

    def test_live_inplaying(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'test_key': 'test_value'}
            response = self.client.get('/api/football/live/inplaying')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'test_key': 'test_value'})

    def test_live_match(self):
        match_id = '123'
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'test_key': 'test_value'}
            response = self.client.get(f'/api/football/live/match/{match_id}')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'test_key': 'test_value'})

    def test_upcoming_matches(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {'test_key': 'test_value'}
            response = self.client.get('/api/football/live/upcoming')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'test_key': 'test_value'})


if __name__ == '__main__':
    unittest.main()
