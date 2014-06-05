# -*- coding: utf-8 -*-
from setuptools import setup
import os
VERSION = open(os.path.join(os.path.dirname(__file__), 'VERSION')).read().strip()

setup(
  name='gigacluster',
  version=VERSION,
  description='ə-lab Gigaword clustering',
  packages=['gigacluster'],
  install_requires=[
      'libschwa-python',
      'nose',
      'beautifulsoup4',
      'requests',
  ],
)
