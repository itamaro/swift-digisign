from setuptools import setup, find_packages

from integ import __version__ as version

name = "integ"

setup(
    name = name,
    version = version,
    author = "Itamar Ostricher",
    author_email = "itamarost <at> gmail <dot> com",
    description = "Integrity",
    license = "Apache License, (2.0)",
    keywords = "openstack swift middleware",
    url = "http://github.com/itamaro/swift-integ",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'paste.filter_factory': [
            'integ=integ.middleware:filter_factory',
            ],
        },
    )