#!/usr/bin/env python

try:
    import setuptools
    from setuptools import setup
except ImportError:
    setuptools = None
    from distutils.core import setup


kwargs = {}

version = "0.1"

if setuptools is not None:
    install_requires = ['requests']
    kwargs['install_requires'] = install_requires

setup(
    name="calamari_client",
    version=version,
    py_modules=["calamari_client"],
    author="Blahhhhh",
    url="https://github.com/Blahhhhh/python-calamari-client/",
    license="https://opensource.org/licenses/MIT",
    description="Ceph Manager API Python Client",
    **kwargs
)