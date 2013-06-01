import sys
import os
from exceptions import Exception
import requests
import cPickle
from Crypto.Hash import SHA

server_ip = '127.0.0.1'
storage_user = 'test:tester'
storage_pass = 'testing'
base_path = os.path.curdir
pubkeys_db_file = os.path.join(base_path, 'public-keys.db')
test_file = os.path.join(base_path, 'test-file.txt')

class OpenStackDemo():
    def __init__(self):
        self.host = server_ip
        self.port = '8080'
        self.user = storage_user
        self.password = storage_pass
        self.container = None
        self.auth_token = None
        self.storage_url = None
        self.public_keys_dict = None

    def _object_url(self, path):
        return '%s/%s/%s' % (self.storage_url, self.container, path)

    def _send_auth_req(self, path, data=None, method=requests.get):
        return method(self._object_url(path).rstrip('/'), data=data,
                      headers={'X-Auth-Token': self.auth_token})
    
    def _sigstr2tuple(self, str):
        return tuple(map(long, str[1:-1].split(', ')))
    
    def get_auth(self):
        # Get AUTH token from OpenStack server
        auth_url = 'http://%s:%s/auth/v1.0' % (self.host, self.port)
        auth_headers = {'X-Storage-User': self.user,
                        'X-Storage-Pass': self.password}
        r = requests.get(auth_url, headers=auth_headers)
        print 'GET auth request returned status %d' % (r.status_code)
        self.auth_token = r.headers['X-Storage-Token']
        self.storage_url = r.headers['X-Storage-URL']
        self.auth_response = r
        return (self.auth_token, self.storage_url, )

    def create_container(self, container='demo-cont'):
        self.container = container
        # check whether container exists
        r = self._send_auth_req('')
        if 404 == r.status_code:
            print 'Creating container "%s"' % (self.container)
            r = self._send_auth_req('', method=requests.put)
            print 'PUT container "%s" returned status %d' % \
                  (self.container, r.status_code)
        self.container_response = r

    def list_contanier(self):
        r = self._send_auth_req('')
        obj_count = int(r.headers['x-container-object-count'])
        print 'Object count in container "%s" is %d' % (self.container, obj_count)
        if 0 < obj_count:
            print r.text
        return r

    def get_object(self, path):
        r = requests.get(self._object_url(path),
                         headers={'X-Auth-Token': self.auth_token})
        print 'GET object "%s" returned status %d' % (path, r.status_code)
        if 200 == r.status_code:
            print 'Content of "%s" object:' % (path)
            print r.content
        self.get_response = r
        return r

    def put_object(self, path, source_file=test_file):
        with open(source_file, 'rb') as f:
            r = requests.put(self._object_url(path), data=f.read(),
                             headers={'X-Auth-Token': self.auth_token})
        print 'PUT object "%s" from file "%s" returned status %d' % \
              (path, source_file, r.status_code)
        self.put_response = r
        return r

    def load_public_keys_dict(self, keys_file=pubkeys_db_file):
        with open(keys_file, 'rb') as f:
            self.public_keys_dict = cPickle.load(f)
        return self.public_keys_dict
    
    def verify_signature(self, obj):
        sig = self._sigstr2tuple(obj.headers['X-Object-Meta-DSA-Signature'])
        sig_user = obj.headers['X-Object-Meta-Sig-User']
        if not sig or not sig_user or not sig_user in self.public_keys_dict:
            raise Exception('Invalid signature metadata or public key DB')
        hash = SHA.new(data=obj.content).digest()
        return self.public_keys_dict[sig_user].verify(hash, sig)

    def tamper(self, path, source_file=test_file):
        r = self.put_object('%s?tamper=1' % (path), source_file)
        r = self.get_object('%s?tamper=1' % (path))
        print 'Tampered DSA signature is %s' %  \
              (r.headers['X-Object-Meta-DSA-Signature'])
        return r

if '__main__' == __name__:
    global demo
    print 'Initializing Demo...'
    demo = OpenStackDemo()
    demo.load_public_keys_dict()
    print 'Getting AUTH token from server'
    demo.get_auth()
    demo.create_container()
    demo.list_contanier()
