# coding=UTF-8

import unittest
from app import app,db,User
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

    def test_send_message(self):
        user = User('alangibson27@gmail.com')
        db.session.add(user)
        db.session.commit()

        form_data = {'name': 'アラン',
                     'email': 'alangibson27@gmail.com',
                     'lessonType': 'レッスン',
                     'otherField': 'otherField',
                     'message': 'アラン'}
        response = self.client.post('/user/%s' % user.uuid, data = form_data)
        self.assert200(response)

    def test_send_message_wrong_user(self):
        form_data = {'name': 'アラン',
                     'email': 'alangibson27@gmail.com',
                     'lessonType': 'レッスン',
                     'otherField': 'otherField',
                     'message': 'アラン'}
        response = self.client.post('/user/z', data = form_data)
        self.assert_status(response, 406)


if __name__ == '__main__':
    unittest.main()