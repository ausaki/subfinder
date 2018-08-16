# -*- coding: utf8 -*-
""" SubFinder的多线程版本
"""

from __future__ import unicode_literals
from .subfinder import SubFinder
try:
    from queue import Queue
except ImportError as e:
    from Queue import Queue
from threading import Thread, Lock

class Pool(object):
    """ 线程池
    """
    def __init__(self, size):
        self.size = size
        self.queue = Queue(maxsize=size)
        self.threads = [Thread(target=self._run) for i in range(size)]
        self._lock = Lock()
        self.start_threads()

    def _acquire(self):
        self._lock.acquire()

    def _release(self):
        self._lock.release()
    
    def start_threads(self):
        for t in self.threads:
            t.daemon = True
            t.start()

    def _run(self):
        while True:
            fn, args, kwargs = self.queue.get()
            fn(*args, **kwargs)
            self.queue.task_done()

    def spawn(self, fn, *args, **kwargs):
        self.queue.put((fn, args, kwargs))
        
    def join(self):
        self.queue.join()

class SubFinderThread(SubFinder):
    """ SubFinder Thread version
    """
    def _init_pool(self):
        self.pool = Pool(10)

