from nose.tools import eq_
from tornado.testing import AsyncHTTPTestCase
from mailsync.app import application

class TestWebApplication(AsyncHTTPTestCase):

    def get_app(self):
        return application

    def test_dashboard(self):
        response = self.fetch('/')
        eq_(response.code, 200)

        response = self.fetch('/dashboard')
        eq_(response.code, 200)

    def test_api(self):
        response = self.fetch('/api')
        eq_(response.code, 200)

    def test_database(self):
        response = self.fetch('/database')
        eq_(response.code, 200)

    def test_column(self):
        response = self.fetch('/columns')
        eq_(response.code, 200)