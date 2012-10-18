#!/usr/bin/env python
from distutils.core import setup
from redtube import __version__

setup(
    name='redtube',
    version=__version__,
    license="BSD",
    description="Python module to access RedTube API",
    author="Don Ramon",
    url="https://github.com/don-ramon/redtube",
    py_modules=["redtube"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.6",
        "License :: OSI Approved :: BSD License",
        "Environment :: Web Environment",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Education",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Multimedia :: Video"
    ],
    keywords='redtube api client',
    install_requires=['python-dateutil', 'simplejson', 'furl']
)