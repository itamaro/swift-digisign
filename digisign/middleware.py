from webob import Response, Request
from swift.common.http import is_success
import cPickle
from Crypto.Hash import SHA
from Crypto import Random
from swift.common.wsgi import make_pre_authed_env, make_pre_authed_request

BACKDOOR = False

g_SigMeta = 'X-Object-Meta-DSA-Signature'
g_SigUserMeta = 'X-Object-Meta-Sig-User'

class SwiftDigisignMiddleware(object):
    """Middleware doing digital signature calculation and verification for Swift objects."""

    def __init__(self, app, conf):
        self.app = app
        with open(conf.get('keys_file'), 'rb') as f:
            self.keys_dict = cPickle.load(f)

    def get_private_key(self, tenant):
        return self.keys_dict[tenant]

    def get_public_key(self, tenant):
        return self.get_private_key(tenant).publickey()

    def __call__(self, env, start_response):
        req = Request(env)
        path_parts = req.path.strip('/').split('/')
        if len(path_parts) < 4:
            # Not handling requests that don't touch objects
            return self.app(env, start_response)
        tenant = req.remote_user.split(',')[1]
        if req.method == 'PUT':
            # Calculate SHA1 digest of content body (160bit)
            hash = SHA.new(req.body).digest()
            # Calculate DSA signature using loaded keys
            sig = self.get_private_key(tenant).sign(hash, Random.new().read(19))
            # Store signature (as string) in object metadata
            if BACKDOOR and ('tamper=1' == req.query_string):
                print 'Tempaer backdoor activated on PUT'
                sig = (sig[0]+1, sig[1]-1)
            req.headers[g_SigMeta] = str(sig)
            req.headers[g_SigUserMeta] = tenant
        if req.method == 'GET' and (not BACKDOOR or 'tamper=1' <> req.query_string):
            # Get the requested object
            resp = make_pre_authed_request(env, 'GET', req.path, agent='SigCheck',
                                           swift_source='SC').get_response(self.app)
            if is_success(resp.status_int):
                verified = False
                # Obtain DSA signature from metadata, if it exists, and verify the content of the object
                if g_SigMeta in resp.headers and g_SigUserMeta in resp.headers:
                    # Calculate SHA1 digest of content body (160bit)
                    hash = SHA.new(resp.body).digest()
                    sig_str = resp.headers[g_SigMeta]
                    sig_user = resp.headers[g_SigUserMeta]
                    sig = tuple(map(long, sig_str[1:-1].split(', ')))
                    verified = self.get_public_key(sig_user).verify(hash, sig)
                if not verified:
                    return Response(status=403, content_type='text/plain',
                                    body='Failed verifying digital signature on '
                                         'requested object')(env, start_response)
        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def digisign_filter(app):
        return SwiftDigisignMiddleware(app, conf)
    return digisign_filter

