import setuptools
from setuptools import setup
from nisnap import __version__
import os.path as op
this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md')) as f:
    long_description = f.read()


download_url = 'https://github.com/xgrg/nisnap/-/archive/v0.4.1/'\
    'nisnap-v0.4.1.tar.gz'


setup(
    name='nisnap',
    install_requires=['coverage>=4.5',
                      'nose>=1.3',
                      'matplotlib>=3.1',
                      'pyxnat>=1.3',
                      'tqdm>=4.31',
                      'nibabel>=2.0',
                      'numpy>=1.16',
                      'urllib3>=1.24',
                      'ipython>=7.3',
                      'Pillow>=7.0',
                      'nilearn>=0.8'],
    scripts=['bin/nisnap'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=__version__,
    description='nisnap',
    packages=setuptools.find_packages(),
    author='Greg Operto',
    author_email='goperto@barcelonabeta.org',
    url='https://github.com/xgrg/nisnap',
    download_url=download_url,
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: Unix',
                 'Programming Language :: Python :: 3.8'],
    package_data={'nisnap': ['utils/colormap.json']})
