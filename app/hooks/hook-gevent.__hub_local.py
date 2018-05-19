import os
import fnmatch
import gevent

gevent_pkg_root = os.path.dirname(gevent.__file__)
modules = []
for f in os.listdir(gevent_pkg_root):
    if fnmatch.fnmatch(f, '_*.py'):
        modules.append('gevent.{}'.format(os.path.splitext(f)[0]))

hiddenimports = [
    'gevent.libuv.loop',
    '_corecffi'
]
hiddenimports.extend(modules)