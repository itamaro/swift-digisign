from setuptools import setup, find_packages

from digisign import __version__ as version

name = "digisign"

setup(
    name = name,
    version = version,
    author = "Itamar Ostricher",
    author_email = "itamarost <at> gmail <dot> com",
    description = "An OpenStack/Swift middleware for digital signature calculation and verification on objects",
    license = "Apache License, (2.0)",
    keywords = "openstack swift middleware",
    url = "http://github.com/itamaro/swift-digisign",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'paste.filter_factory': [
            'digisign=digisign.middleware:filter_factory',
            ],
        },
    )
