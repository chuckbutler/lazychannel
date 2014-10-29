from distutils.core import setup
from setuptools import find_packages

setup(
    name="lazychannel",
    version="1.0.0",
    description="Fetch things daily!",
    license="LGPLv3",
    install_requires=[
        'requests',
        'gdata',
    ],
)
