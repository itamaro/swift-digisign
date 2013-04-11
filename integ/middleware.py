from webob import Response
from swift.common.swob import Request
from swift.common.utils import get_logger

class SwiftIntegrityMiddleware(object):
    """Middleware doing virus scan for Swift."""

    def __init__(self, app, conf):
        # app is the final application
        self.app = app
        self.logger = get_logger(conf, log_route='proxy-server')

    def __call__(self, env, start_response):
        req = Request(env)
        req.headers['x-object-meta-foo'] = 'bar'
        print "weeeeeeeeee"
        #if env['REQUEST_METHOD'] == 'PUT':
        #    env['X-Object-Meta-Foo'] = 'bar'
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def integrity_filter(app):
        return SwiftIntegrityMiddleware(app, conf)
    return integrity_filter
