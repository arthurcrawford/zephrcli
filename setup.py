from setuptools import setup
import os

with open(os.path.join('.', 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

setup(
    name='zephr',
    version=__version__,
    py_modules=['zephr', 'api_auth'],
    install_requires=[
        'click',
        'requests',
        'keyring',
        'pwinput'
    ],
    entry_points={
        'console_scripts': [
            'zephr = zephr:cli',
        ],
    },
)
