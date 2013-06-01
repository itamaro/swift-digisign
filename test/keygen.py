import sys
import os
import cPickle
from Crypto.Random import random
from Crypto.PublicKey import DSA
from Crypto.Hash import SHA

tenants = ['test:tester', 'test2:tester2', 'test3:tester3']
base_path = '/base/path/for/output'
keys_file = os.path.join(base_path, 'keys.db')
public_keys_file = os.path.join(base_path, 'public-keys.db')

keys_dict = {}
public_dict = {}

def build_keydict():
    for tenant in tenants:
        print 'Generating DSA keys for tenant "%s"' % (tenant)
        full_key = DSA.generate(1024)
        keys_dict[tenant] = full_key

def derive_public_keydict():
    for tenant, full_key in keys_dict.iteritems():
        print 'Deriving public keys for tenant "%s"' % (tenant)
        public_dict[tenant] = full_key.publickey()

def dump_dicts():
    for dump_file, kdict in [(keys_file, keys_dict),
                             (public_keys_file, public_dict)]:
        with open(dump_file, 'wb') as f:
            cPickle.dump(kdict, f)

if '__main__' == __name__:
    build_keydict()
    derive_public_keydict()
    dump_dicts()
