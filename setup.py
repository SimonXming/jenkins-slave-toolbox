#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import os
import re
import sys

from setuptools import find_packages
from setuptools import setup


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


install_requires = [
    # 'cached-property >= 1.2.0, < 2',
    'docopt >= 0.6.1, < 0.7',
    # 'PyYAML >= 3.10, < 4',
    # 'requests >= 2.6.1, != 2.11.0, < 2.12',
    # 'texttable >= 0.8.1, < 0.9',
    # 'websocket-client >= 0.32.0, < 1.0',
    # 'docker-py >= 1.10.4, < 2.0',
    # 'dockerpty >= 0.4.1, < 0.5',
    # 'six >= 1.3.0, < 2',
    # 'jsonschema >= 2.5.1, < 3',
]


tests_require = [
    # 'pytest',
]

setup(
    name='jk-toolbox',
    version=find_version("jk_toolbox", "__init__.py"),
    description='DNT dcos CICD service jenkins slave toolbox.',
    url='https://www.docker.com/',
    author='SimonShyu',
    license='Apache License 2.0',
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    # test_suite='nose.collector',
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points="""
    [console_scripts]
    jk-toolbox=jk_toolbox.cli.main:main
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)