from setuptools import setup

setup(
    name='zephr',
    version='0.1.5',
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
