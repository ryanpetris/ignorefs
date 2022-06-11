#!/usr/bin/env python3

import errno
import fcntl
import os


class PassthroughFile(object):
    def __init__(self, path, flags, *mode):
        self.file = os.fdopen(os.open("." + path, flags, *mode), self._flag2mode(flags))
        self.fd = self.file.fileno()

    def read(self, length, offset):
        return os.pread(self.fd, length, offset)

    def write(self, buf, offset):
        return os.pwrite(self.fd, buf, offset)

    def release(self, flags):
        self.file.close()

    def fsync(self, isfsyncfile):
        self._fflush()

        if isfsyncfile and hasattr(os, 'fdatasync'):
            os.fdatasync(self.fd)
        else:
            os.fsync(self.fd)

    def flush(self):
        self._fflush()

        os.close(os.dup(self.fd))

    def fgetattr(self):
        return os.fstat(self.fd)

    def ftruncate(self, length):
        self.file.truncate(length)

    def lock(self, cmd, owner, **kw):
        op = {fcntl.F_UNLCK: fcntl.LOCK_UN,
              fcntl.F_RDLCK: fcntl.LOCK_SH,
              fcntl.F_WRLCK: fcntl.LOCK_EX}[kw['l_type']]

        if cmd == fcntl.F_GETLK:
            return -errno.EOPNOTSUPP
        elif cmd == fcntl.F_SETLK:
            if op != fcntl.LOCK_UN:
                op |= fcntl.LOCK_NB
        elif cmd == fcntl.F_SETLKW:
            pass
        else:
            return -errno.EINVAL

        fcntl.lockf(self.fd, op, kw['l_start'], kw['l_len'])

    def _flag2mode(self, flags):
        md = {os.O_RDONLY: 'rb', os.O_WRONLY: 'wb', os.O_RDWR: 'wb+'}
        m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

        if flags | os.O_APPEND:
            m = m.replace('w', 'a', 1)

        return m

    def _fflush(self):
        if 'w' in self.file.mode or 'a' in self.file.mode:
            self.file.flush()
