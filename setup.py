from setuptools import setup
import os

with open(os.path.join('.', 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='zephr',
    version=version,
    py_modules=['zephr', 'api_auth', 'config'],
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
