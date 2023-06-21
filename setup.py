from setuptools import setup

setup(
    name='zephr',
    version='0.1.1',
    py_modules=['zephr'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'zephr = zephr:cli',
        ],
    },
)
