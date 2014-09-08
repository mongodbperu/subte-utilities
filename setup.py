# -*- coding: utf-8 *-*
import os
import subprocess
import sys

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

from distutils.cmd import Command


with open('README.rst') as f:
    readme_content = f.read()


setup(
    name='subte',
    version='0.0+',
    url='https://github.com/MongoDBPeru/subte',
    description='Utilities for Subte project.',
    long_description=readme_content,
    author='MongoDB Perú',
    author_email='info@mongodbperu.com',
    packages=['subte'],
    keywords=['subte', 'mongodb', 'university', 'courses', 'translation',
              'utilities'],
    install_requires=['pymongo'],
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'],
    entry_points={
        'console_scripts': [
            'subte-gen = subte.generator:main',
        ],
    },
    test_suite='tests.runtests',
)
