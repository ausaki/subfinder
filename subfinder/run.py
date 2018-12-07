# -*- coding: utf8 -*-
""" 命令行入口
"""
from __future__ import unicode_literals, print_function
import sys
import time
import argparse
import six
from .subsearcher import get_subsearcher, get_all_subsearchers, BaseSubSearcher
from .subfinder import SubFinder
from . import __version__


def find_method(m):
    s = get_subsearcher(m)
    if s is None:
        raise argparse.ArgumentTypeError(
            'Cant found SubSearcher named {}'.format(m))
    return s


def method_msg():
    all_subsearchers = get_all_subsearchers()
    support_methods = ', '.join(all_subsearchers.keys())
    default_subsearcher = get_subsearcher('default')
    msg = '''what's methods you want to use to searching subtitles, defaults to {default}.
            support methods: {support_methods}
        '''.format(default=default_subsearcher.__name__, support_methods=support_methods)
    return msg


def epilog():
    all_subsearchers = get_all_subsearchers()
    msg = 'Languages & Exts\n\n'
    for name, subsearcher in all_subsearchers.items():
        msg += 'languages supported by {}: {}\n'.format(
            name, subsearcher.SUPPORT_LANGUAGES)
        msg += 'exts supported by {}: {}\n'.format(
            name, subsearcher.SUPPORT_EXTS)
        msg += '\n'
    return msg


def run(subfinder_class):
    parser = argparse.ArgumentParser(prog='subfinder',
                                     description='A general subfinder, support for custom subsearcher',
                                     epilog=epilog(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )
    parser.add_argument(
        'path', help="the video's filename or the directory contains vedio files")
    parser.add_argument('-l', '--languages',
                        nargs='+',
                        help="what's languages of subtitle you want to find")
    parser.add_argument('-e', '--exts',
                        nargs='+',
                        help="what's formats of subtitle you want to find")
    parser.add_argument('-m', '--method',
                        nargs='+', type=find_method, default='default',
                        help=method_msg())
    parser.add_argument('-s', '--silence',
                        action='store_true', default=False,
                        help="don't print anything, default to False")
    parser.add_argument('-p', '--pause',
                        action='store_true', default=False,
                        help="pause script after subfinder done. this option is used in 'Context Menu on Windows' only")
    parser.add_argument('-v', '--version',
                        action='version', version='subfinder {v}'.format(v=__version__),
                        help="show subfinder's version")
    parser.add_argument('--debug',
                        action='store_true', default=False,
                        help="print debug infomation, default to False")

    args = parser.parse_args()
    
    # try to make `path` to unicode string in python2
    if six.PY2 and isinstance(args.path, six.binary_type):
        args.path = args.path.decode(sys.getfilesystemencoding())

    subfinder = subfinder_class(path=args.path,
                                languages=args.languages,
                                exts=args.exts,
                                subsearcher_class=args.method,
                                silence=args.silence,
                                debug=args.debug)
    subfinder.start()
    subfinder.done()

    if args.pause:
        time.sleep(5)


if __name__ == '__main__':
    run(SubFinder)
