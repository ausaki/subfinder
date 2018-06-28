# -*- coding: utf8 -*-
from .subfinder_thread import SubFinderThread as SubFinder
from .run import run as run_


def run():
    run_(SubFinder)


if __name__ == '__main__':
    run()