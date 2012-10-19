#!/usr/bin/env python
from distutils.core import setup
from redtube import __version__

setup(
    name='redtube',
    version=__version__,
    license="BSD",
    description="Python module to access RedTube API",
    long_description="".join(open('README.rst').readlines()),
    author="Don Ramon",
    url="https://github.com/don-ramon/redtube",
    py_modules=["redtube"],
    entry_points={'console_scripts': [
        'redtube-search = redtube:main'
    ]},
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
    keywords='redtube api client'
)