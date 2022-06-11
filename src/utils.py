#!/usr/bin/env python3

import errno
import os


def cleanpath(path):
    return os.path.join('..', os.path.relpath(path, '/'))


def pathcheck(func):
    def wrap(self, path, *args, **kwargs):
        if self.spec.match_file(path):
            return -errno.ENOENT

        return func(self, path, *args, **kwargs)

    return wrap
