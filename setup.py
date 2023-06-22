from setuptools import setup

setup(
    name='zephr',
    version='0.1.13',
    packages=['zephrcli'],
    data_files=[('zephrcli', ['VERSION'])],
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
