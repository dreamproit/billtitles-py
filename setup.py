from setuptools import setup
import sys

sys.path[0:0] = ['billtitles']

from version import __version__

setup(
    name='billtitles',
    version=__version__,
    packages=['billtitles'],
    install_requires=[
        'importlib; python_version == "3.8"',
    ],
)
