# -*- coding: utf8 -*-
from gevent import monkey;monkey.patch_all()
import argparse
from .subfinder_gevent import SubFinderGevent
from .subsearcher import *

def find_method(m):
    g = globals()
    method = g.get(m)
    return method


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path', help="the video's filename or the directory contains vedio files")
    parser.add_argument('-l', '--languages',
                        nargs='+',
                        help="what's languages of subtitle you want to find")
    parser.add_argument('-e', '--exts',
                        nargs='+',
                        help="what's format of subtitle you want to find")
    parser.add_argument('-m', '--method',
                        type=find_method, default=ShooterSubSearcher,
                        help='''what's method you want to use to searching subtitles, defaults to ShooterSubSearcher.
                        only support ShooterSubSearcher for now.
                        ''')
    parser.add_argument('-s', '--silence',
                        action='store_true', default=False,
                        help="don't print anything, default to False")

    args = parser.parse_args()
    if args.method is None:
        args.method = ShooterSubSearcher

    subfinder = SubFinderGevent(path=args.path,
                          languages=args.languages,
                          exts=args.exts,
                          subsearcher_class=args.method,
                          silence=args.silence)
    subfinder.start()
    subfinder.done()

if __name__ == '__main__':
    run()