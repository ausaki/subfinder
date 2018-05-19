# -*- coding: utf8 -*-
from gevent import monkey;monkey.patch_all()
from .run import run
from .subfinder_gevent import SubFinderGevent as SubFinder

if __name__ == '__main__':
    run(SubFinder)