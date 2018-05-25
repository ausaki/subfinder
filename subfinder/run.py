# -*- coding: utf8 -*-
from __future__ import unicode_literals
import sys
import argparse
from .subsearcher import get_subsearcher, get_all_subsearchers
from .subfinder import SubFinder
import time


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
                                     description='A general subsearcher, support for custom SubSearcher',
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

    args = parser.parse_args()

    if args.languages:
        args.method._check_languages(args.languages)
    if args.exts:
        args.method._check_exts(args.exts)

    # try to decode str to unicode in python2
    try:
        args.path = args.path.decode(sys.getfilesystemencoding())
    except AttributeError as e:
        pass

    subfinder = subfinder_class(path=args.path,
                                languages=args.languages,
                                exts=args.exts,
                                subsearcher_class=args.method,
                                silence=args.silence)
    subfinder.start()
    subfinder.done()

    if args.pause:
        time.sleep(5)


if __name__ == '__main__':
    run(SubFinder)
