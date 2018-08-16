# -*- coding: utf8 -*-
""" 命令行入口的协程版本
"""
from gevent import monkey;monkey.patch_all()
from .run import run as run_
from .subfinder_gevent import SubFinderGevent as SubFinder


def run():
    run_(SubFinder)


if __name__ == '__main__':
    run()