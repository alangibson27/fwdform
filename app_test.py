import unittest
from app import app,db
from flask.ext.testing import TestCase

class AppTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.create_all()
        return app

    def test_registration_enabled(self):
        app.config['REGISTRATION_ENABLED'] = 'True'
        registration_request = {'email': 'testuser@example.com'}
        response = self.client.post('/register', data = registration_request)
        self.assert200(response)
        self.assertTrue(response.get_data().startswith('Token:'))

    def test_registration_disabled(self):
        app.config['REGISTRATION_ENABLED'] = 'False'
        registration_request = {'email': 'testuser@example.com'}
        response = self.client.post('/register', data = registration_request)
        self.assert403(response)

if __name__ == '__main__':
    unittest.main()