from setuptools import setup
import importlib.resources

# Load version from VERSION file
version = importlib.resources.read_text('zephrcli', "VERSION")

setup(
    name='zephrcli',
    version=version,
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
