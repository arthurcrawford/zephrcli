from setuptools import setup

from config import VERSION_FILE

with open(VERSION_FILE) as version_file:
    version = version_file.read().strip()

setup(
    name='zephr',
    version=version,
    py_modules=['zephr', 'api_auth', 'config'],
    include_package_data=True,
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
