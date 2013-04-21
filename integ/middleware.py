from webob import Response, Request
import cPickle
from Crypto.Hash import SHA
from Crypto import Random

class SwiftIntegrityMiddleware(object):
    """Middleware doing virus scan for Swift."""

    def __init__(self, app, conf):
        # app is the final application
        self.app = app
        with open(conf.get('dsa_key_file'), 'rb') as f:
            self.dsa_key = cPickle.load(f)


    def __call__(self, env, start_response):
        req = Request(env)
        print "weeeeeeeeee-21-04--3"
        if req.method == 'PUT':
            # Calculate SHA1 digest of content body (160bit)
            hash = SHA.new(req.body).digest()
            # Calculate DSA signature using loaded keys
            sig = self.dsa_key.sign(hash, Random.new().read(19))
            # Store signature (as string) in object metadata
            req.headers['x-object-meta-dsa-signature'] = str(sig)
        if req.method == 'GET':
            # Obtain DSA signature from metadata, if it exists, and verify the content of the object
            if 'x-object-meta-dsa-signature' in req.headers:
                sig_str = req.headers['x-object-meta-dsa-signature']
                sig = tuple(map(long, sig_str[1:-1].split(', ')))
                #self.dsa_key.verify(
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def integrity_filter(app):
        return SwiftIntegrityMiddleware(app, conf)
    return integrity_filter

