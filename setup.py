from setuptools import setup
import os

version = 'Unknown'
try:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    VERSION_PATH = os.path.join(ROOT_DIR, 'src/zephrcli')
    # Can't open VERSION file as resource at this point - have to open from file system
    with open(os.path.join(VERSION_PATH, 'VERSION')) as version_file:
        version = version_file.read().strip()
except Exception as e:
    raise 'An error occurred reading VERSION file'

setup(
    name='zephrcli',
    version=version,
    package_dir={'': 'src'},
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
