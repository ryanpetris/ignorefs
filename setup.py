#!/usr/bin/env python

import os

from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r") as rf:
    requirements = rf.read().splitlines(False)

setup(
    name='IgnoreFS',
    version='1.0',
    description='FUSE filesystem that hides/ignores files and directories based on an ignore file.',
    author='Ryan Petris',
    author_email='ryan@petris.net',
    url='https://github.com/ryanpetris/ignorefs',
    packages=['ignorefs'],
    package_dir={'ignorefs': 'src'},
    install_requires=requirements,
    license='LGPL',
    platforms=['posix'],
)
