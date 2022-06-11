#!/usr/bin/env python3

import fuse

from .ignore_fs import IgnoreFS

fuse.fuse_python_api = (0, 2)
fuse.feature_assert('stateful_files', 'has_init')

usage = """IgnoreFS: mirror a filesystem and apply ignore rules.
ignorefs [source] [mountpoint] [options]"""

server = IgnoreFS(
    version="%prog " + fuse.__version__,
    usage=usage,
    dash_s_do='setsingle'
)

server.main()
