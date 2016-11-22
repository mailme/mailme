#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os

from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


test_requires = [
    # General test libraries
    'tox==2.5.0',
    'pytest==3.0.4',
    'pytest-django==3.1.1',
    'pytest-isort==0.1.0',

    'tzlocal==1.2.2',

    # Pep8 and code quality checkers
    'flake8==3.2.1',
    'pytest-cov==2.2.1',
    'coverage==4.2',

    # Fixtures, test helpers
    'factory-boy==2.7.0',
    'mock==2.0.0',
]


install_requires = [
    # General dependencies
    'django==1.10.3',

    # Imap utilities
    'dnspython3==1.12.0',
    'imapclient==1.0.2',

    # For async worker support
    'celery==4.0.0',

    # i18n/l10n,
    'babel==2.3.4',
    'django-babel==0.5.1',

    # For our REST Api
    'djangorestframework==3.5.3',
    'PyJWT==1.4.2',
    'requests==2.9.1',
    'urllib3==1.19.1',
    'requests-toolbelt==0.7.0',

    # For proper timezone support.
    'pytz==2016.7',

    # Charset detection
    'chardet==2.3.0'
]


docs_requires = [
    'sphinx==1.4.8',
    'sphinx_rtd_theme'
]


postgresql_requires = [
    'psycopg2==2.6.2',
]


redis_requires = [
    'redis==2.10.5',
]

setup(
    name='mailme',
    version='0.1.0',
    description='manage those mailboxes!',
    long_description=read('README.rst') + '\n\n' + read('CHANGES.rst'),
    author='Christopher Grebs',
    author_email='cg@webshox.org',
    url='https://github.com/mailme/mailme/',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    test_suite='src',
    tests_require=test_requires,
    install_requires=install_requires,
    extras_require={
        'docs': docs_requires,
        'tests': test_requires,
        'postgresql': postgresql_requires,
        'redis': redis_requires,
    },
    zip_safe=False,
    entry_points={},
    license='BSD',
    classifiers=[
        '__DO NOT UPLOAD__',
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
