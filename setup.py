from setuptools import setup, find_packages, Extension
import sys
import os
import platform
from distutils.sysconfig import get_config_var
from distutils.version import LooseVersion

PACKAGENAME = "CHECLabPySB"
DESCRIPTION = ("Sandbox package for personal scripts "
               "primarily using the CHECLabPy Package")
AUTHOR = "Jason J Watson"
AUTHOR_EMAIL = "jason.watson@physics.ox.ac.uk"
VERSION = "1.0.0"

extensions = [
    Extension(
        'CHECLabPySB.d190209_spectra.spe_functions',
        sources=['CHECLabPySB/d190209_spectra/spe_functions.cc'],
    ),
]

def is_platform_mac():
    return sys.platform == 'darwin'

# Handle mac error: https://github.com/pandas-dev/pandas/issues/23424
if is_platform_mac():
    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_system = LooseVersion(platform.mac_ver()[0])
        python_target = LooseVersion(
            get_config_var('MACOSX_DEPLOYMENT_TARGET'))
        if python_target < '10.9' and current_system >= '10.9':
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'
            os.environ['CC'] = 'clang'
            os.environ['CXX'] = 'clang++'

setup(
    name=PACKAGENAME,
    packages=find_packages(),
    version=VERSION,
    description=DESCRIPTION,
    license='BSD3',
    install_requires=[
        'astropy',
        'scipy',
        'numpy',
        'matplotlib',
        'tqdm',
        'pandas>=0.21.0',
        'iminuit',
        'numba',
        'PyYAML', 'seaborn'
    ],
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    package_data={
        '': ['data/*'],
    },
    ext_modules=extensions,
)
