#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os

from setuptools import find_packages, setup


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


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
    tests_require=[],
    install_requires=[],
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
        'Programming Language :: Python :: 3.6',
    ],
)
