#!/usr/bin/env python

from distutils.core import setup

version = '0.1'

classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='django-fieldlevel-permissions',
    version=version,
    url='http://github.com/cpharmston/django-fieldlevel-permissions',
    author='Chuck Harmston',
    author_email='chuck@chuckharmston.com',
    license='Dual-licensed under MIT and GPL',
    packages=['fieldlevel'],
    package_dir={'fieldlevel': 'fieldlevel'},
    description=(
        'A subclass of ModelAdmin that provides hooks for setting field-level '
        'permissions based on object or request properties.'
    ),
    classifiers=classifiers,
)