from webob import Response, Request
from swift.common.swob import Request as SwobReq
from swift.common.utils import get_logger

class SwiftIntegrityMiddleware(object):
    """Middleware doing virus scan for Swift."""

    def __init__(self, app, conf):
        # app is the final application
        self.app = app
        self.logger = get_logger(conf, log_route='proxy-server')

    def __call__(self, env, start_response):
        swobreq = SwobReq(env)
        req = Request(env)
        #req.headers['x-object-meta-foo'] = 'bar'
        print "weeeeeeeeee-18-04--1"
        #print repr(env)
        if env['REQUEST_METHOD'] == 'PUT':
            #print 'type(env)', type(env)
            #print 'type(req)', type(req)
            #print 'type(req-method)', type(env['REQUEST_METHOD'])
            #print 'read env(wsgi.input)', env['wsgi.input'].read()
            print 'req.method', req.method
            print 'req.body', req.body
            swobreq.headers['x-object-meta-foobar'] = 'barfoo'
            #swobreq.headers['x-object-meta-content'] = env['wsgi.input'].read()
        #    env['X-Object-Meta-Foo'] = 'bar'
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def integrity_filter(app):
        return SwiftIntegrityMiddleware(app, conf)
    return integrity_filter
