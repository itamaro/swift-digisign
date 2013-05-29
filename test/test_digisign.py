import unittest
from webob import Request, Response

from integ.middleware import SwiftDigisignMiddleware

class FakeApp(object):
    def __call__(self, env, start_response):
        return Response(body="FAKE APP")(env, start_response)


class TestSwiftDigisignMiddleware(unittest.TestCase):
 
    def setUp(self):
        self.app = SwiftDigisignMiddleware(FakeApp(), {})

    def test_simple_request(self):
        resp = Request.blank('/',
                             environ={
                                 'REQUEST_METHOD': 'GET',
                             }).get_response(self.app)
        self.assertEqual(resp.body, "FAKE APP")

if __name__ == '__main__':
    unittest.main()
