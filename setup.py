#!python
# -*- coding: UTF-8 -*-
"""
Setup script for building sqlautocode
"""
from setuptools import setup, find_packages

__version__ = '0.6b1'


setup(
    name='sqlautocode',
    version=__version__,
    description=(
        'AutoCode is a flexible tool to autogenerate'
        'a model from an existing database.'
    ),
    author='Simon Pamies',
    author_email='s.pamies@banality.de',
    url='http://code.google.com/p/sqlautocode/',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    zip_safe=True,
    license='MIT',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
    ],
    entry_points=dict(
        console_scripts=[
            'sqlautocode = sqlautocode.main:main',
        ],
    ),
    install_requires=[
        'sqlalchemy'  # XXX What's our minimum supported version??
    ],
    include_package_data=True,
    tests_require=[
        'nose>=0.10',
    ],
    test_suite="nose.collector",
)
