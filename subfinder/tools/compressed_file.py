# -*- coding: utf-8 -*-
""" 解压压缩包，支持zip, rar
"""
import os
import sys
import six

class CompressedFile(object):
    """ a simple wrapper class for ZipFile and RarFile, it's only support read.
    """
    EXTS = ['zip', 'rar']

    def __init__(self, file):
        self.file = file
        self._file = None
        _, ext = os.path.splitext(file)
        if ext == '.zip':
            import zipfile
            self._file = zipfile.ZipFile(self.file, 'r')
        elif ext == '.rar':
            import rarfile
            if sys.platform == 'win32':
                # if os system is windows，try to use built-in unrar
                rarfile.UNRAR_TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unrar.exe')
            self._file = rarfile.RarFile(self.file, 'r')
        else:
            raise ValueError('CompressedFile doesnt support "{}"'.format(ext))

    @staticmethod
    def decode_file_name(name):
        if six.PY3:
            try:
                name = name.encode('cp437')
            except UnicodeEncodeError as e:
                pass
        if isinstance(name, six.binary_type):
            try:
                name = name.decode('gbk')
            except UnicodeDecodeError as e:
                try:
                    name = name.decode('utf8')
                except UnicodeDecodeError as e:
                    pass
        return name

    @classmethod
    def is_compressed_file(cls, filename):
        _, ext = os.path.splitext(filename)
        ext = ext[1:]
        return ext in cls.EXTS

    def isdir(self, name):
        info = self._file.getinfo(name)
        try:
            return info.isdir()
        except:
            return name.endswith(os.path.sep)

    def namelist(self):
        return self._file.namelist()

    def extract(self, filename, dest):
        f = self._file.open(filename, 'r')
        with open(dest, 'wb') as fp:
            fp.write(f.read())

    def close(self):
        self._file.close()