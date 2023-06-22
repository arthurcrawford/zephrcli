from setuptools import setup
import importlib.resources
import os

# Load version from VERSION file
# version = importlib.resources.read_text('zephrcli', "VERSION")
# version = '0.1.24'
print(f'Setup.py - CWD: {os.getcwd()}')
print(f'Setup.py - __file__: {__file__}')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
print(f'Setup.py - ROOT_DIR: {ROOT_DIR}')
VERSION_PATH = os.path.join(ROOT_DIR, 'src/zephrcli')
print(f'Setup.py - ROOT_DIR: {VERSION_PATH}')
version = 'Unknown'
try:
    with open(os.path.join(VERSION_PATH, 'VERSION')) as version_file:
        version = version_file.read().strip()
    # No packages yet so can't do this
    test = importlib.resources.read_text('zephrcli', "VERSION")
except Exception as e:
    raise 'An error occurred reading VERSION file'
print(f'Setup.py - Version: {version}')

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
