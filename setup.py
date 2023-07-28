#!/bin/env python
# encoding: utf-8

import os
import re

from setuptools import setup
from setuptools import find_packages

v = open(os.path.join(os.path.dirname(__file__), "mlsync", "__init__.py"))
VERSION = re.compile(r".*__version__ = \"(.*?)\"", re.S).match(v.read()).group(1)

setup(
    name="inknews",
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "spyne",
        "readability-lxml",
        "pycurl",
        "neurons",
        "lxml",
        "twisted",
        "beautifulsoup4",
    ],
    package_data={},
    entry_points={"console_scripts": ["mlsync=mlsync.main:main",],},
    author="Arskom Ltd.",
    author_email="burak.arslan@arskom.com.tr",
    description="Mailing List Synchronizer",
)
