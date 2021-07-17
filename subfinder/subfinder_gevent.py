# -*- coding: utf8 -*-
""" SunFinder 的协程版本
"""

from gevent.pool import Pool
from .subfinder import SubFinder


class SubFinderGevent(SubFinder):
    """SubFinder Thread version"""

    def _init_pool(self):
        self.pool = Pool(10)
