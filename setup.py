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
      'scikit-learn',
  ],
  setup_requires=[
    'setuptools_git >= 0.3',
  ],
  include_package_data=True,
)
