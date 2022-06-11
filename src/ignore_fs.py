#!/usr/bin/env python3

import fuse
import errno
import os
import pathspec
import sys

from .passthrough_file import PassthroughFile
from .utils import cleanpath, pathcheck


class IgnoreFS(fuse.Fuse):
    def __init__(self, *args, **kwargs):
        fuse.Fuse.__init__(self, *args, **kwargs)

        self.file_class = PassthroughFile
        self.root = '/'
        self.match_file = None

        self.parser.add_option(mountopt="match_file", metavar="FILE", help="file that contains matches (.gitignore syntax)")
        self.parse(values=self, errex=1)

        self.fuse_args.optdict.setdefault('subtype', 'ignorefs')

        spec_lines = []

        if self.match_file:
            with open(self.match_file, 'r') as file:
                spec_lines = file.readlines()

        self.spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, spec_lines)

        try:
            if self.fuse_args.mount_expected():
                _, cmdline = self.cmdline
                self.root = cmdline.pop()
                self.fuse_args.optdict.setdefault('fsname', os.path.abspath(self.root))
                self.fsinit()
        except OSError:
            print("can't enter root of underlying filesystem", file=sys.stderr)
            sys.exit(1)

    @pathcheck
    def getattr(self, path):
        return os.lstat(cleanpath(path))

    @pathcheck
    def readlink(self, path):
        return os.readlink(cleanpath(path))

    @pathcheck
    def readdir(self, path, offset):
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')

        for e in os.listdir(cleanpath(path)):
            file_path = os.path.join(path, e)

            if self.spec.match_file(file_path):
                continue

            yield fuse.Direntry(e)

    @pathcheck
    def unlink(self, path):
        os.unlink(cleanpath(path))

    @pathcheck
    def rmdir(self, path):
        os.rmdir(cleanpath(path))

    @pathcheck
    def symlink(self, path, path1):
        os.symlink(cleanpath(path), cleanpath(path1))

    @pathcheck
    def rename(self, path, path1):
        os.rename(cleanpath(path), cleanpath(path1))

    @pathcheck
    def link(self, path, path1):
        os.link(cleanpath(path), cleanpath(path1))

    @pathcheck
    def chmod(self, path, mode):
        os.chmod(cleanpath(path), mode)

    @pathcheck
    def chown(self, path, user, group):
        os.chown(cleanpath(path), user, group)

    @pathcheck
    def truncate(self, path, length):
        f = open(cleanpath(path), "a")
        f.truncate(length)
        f.close()

    @pathcheck
    def mknod(self, path, mode, dev):
        os.mknod(cleanpath(path), mode, dev)

    @pathcheck
    def mkdir(self, path, mode):
        os.mkdir(cleanpath(path), mode)

    @pathcheck
    def utime(self, path, times):
        os.utime(cleanpath(path), times)

    @pathcheck
    def access(self, path, mode):
        if not os.access(cleanpath(path), mode):
            return -errno.EACCES

    def statfs(self):
        return os.statvfs("..")

    def fsinit(self):
        os.chdir(self.root)
