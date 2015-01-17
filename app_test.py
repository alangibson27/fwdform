# coding=UTF-8

import app
import unittest
import flask

class MessageBuilderTest(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)

    def test_build_message_with_extra_fields(self):
        form_data = dict(
            name = "Alan",
            email = "alangibson27@gmail.com",
            lessonType = "%E3%83%97%E3%83%A9%E3%82%A4%E3%83%99%E3%83%BC%E3%83%88%E3%83%AC%E3%83%83%E3%82%B9%E3%83%B3",
            message = "aaaa")

        with self.app.test_request_context("/", data = form_data, content_type = "application/x-www-form-urlencoded"):
            msg = app.build_message(app.User("me@example.com"), flask.request)

            self.assertEquals(
                msg['text'],
                u"lessonType: %E3%83%97%E3%83%A9%E3%82%A4%E3%83%99%E3%83%BC%E3%83%88%E3%83%AC%E3%83%83%E3%82%B9%E3%83%B3\naaaa")