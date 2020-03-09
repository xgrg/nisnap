import setuptools
from setuptools import setup

import os.path as op
this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md')) as f:
    long_description = f.read()
from nisnap import __version__

setup(
  name = 'nisnap',
  install_requires=['coverage>=4.5',
    'nose>=1.3',
    'matplotlib>=3.1',
    'pyxnat>=1.2.1.0.post3',
    'tqdm>=4.31',
    'nibabel>=2.3',
    'numpy>=1.16',
    'urllib3>=1.24',
    'ipython>=7.3'],
  scripts=['bin/nisnap'],
  long_description=long_description,
  long_description_content_type='text/markdown',
  version = __version__,
  description = 'nisnap',
  packages=setuptools.find_packages(),
  author = 'Greg Operto',
  author_email = 'goperto@barcelonabeta.org',
  url = 'https://gitlab.com/xgrg/nisnap',
  download_url = 'https://gitlab.com/xgrg/nisnap/-/archive/v0.1/nisnap-v0.1.tar.gz',
  classifiers = ['Intended Audience :: Science/Research',
      'Intended Audience :: Developers',
      'Topic :: Scientific/Engineering',
      'Operating System :: Unix',
      'Programming Language :: Python :: 3.7' ],
  package_data={'nisnap': [ 'requirements.txt', 'README.md'], },
)
