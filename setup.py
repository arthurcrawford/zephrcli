from setuptools import setup

setup(
    name='zephrcli',
    version='0.1.13',
    package_dir={'':'src'},
    packages=['zephrcli'],
    package_data={'zephrcli': ['VERSION']},
    install_requires=[
        'click',
        'requests',
        'keyring',
        'pwinput'
    ],
    entry_points={
        'console_scripts': [
            'zephr = zephrcli.zephr:cli',
        ],
    },
)
