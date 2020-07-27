# -*- coding: utf8 -*-
""" 命令行入口
"""
from __future__ import unicode_literals, print_function
import os
import sys
import time
import argparse
import six
import json
from .subsearcher import get_subsearcher, get_all_subsearchers, BaseSubSearcher
from .subfinder import SubFinder
from . import __version__


def find_method(m):
    s = get_subsearcher(m)
    if s is None:
        raise argparse.ArgumentTypeError( 'Cant found SubSearcher named {}'.format(m))
    return s


def method_msg():
    all_subsearchers = get_all_subsearchers()
    support_methods = ', '.join(all_subsearchers.keys())
    default_subsearcher = get_subsearcher('default')
    msg = '''methods use to search subtitles, default is using all methods.
            support methods: {support_methods}
        '''.format(support_methods=support_methods)
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
                                     description='A general subfinder, support custom subsearcher',
                                     epilog=epilog(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )
    parser.add_argument(
        'path', help="the path of video file, or the directory contains video files")
    parser.add_argument('-l', '--languages',
                        nargs='+',
                        help="specify what subtitle languages you want")
    parser.add_argument('-e', '--exts',
                        nargs='+',
                        help="specify what subtitle formats you want")
    parser.add_argument('-m', '--method',
                        nargs='+', type=find_method,
                        help=method_msg())
    parser.add_argument('-k', '--keyword',
                        help='keyworkd for the video using to search on the subtitle website')
    parser.add_argument('-c', '--conf', default='~/.subfinder.json',
                        help='configuration file')
    parser.add_argument('--video_exts',
                        nargs='+',
                        help='the extensions of video file(include ".", e.g: .mp4)')
    parser.add_argument('--ignore',
                        action='store_true',
                        help='search subtitles even there are existing subtitles')
    parser.add_argument('-x', '--exclude',
                        nargs='+',
                        help='exclude files and directorys, support glob mode like shell, e.g *, ?')
    parser.add_argument('--api_urls',
                        type=json.loads,
                        help="specify the api urls with JSON")
    parser.add_argument('-s', '--silence',
                        action='store_true',
                        help="don't print anything, default to False")
    parser.add_argument('-p', '--pause',
                        action='store_true',
                        help="pause script after subfinder done. this option is used in 'Context Menu on Windows' only")
    parser.add_argument('-v', '--version',
                        action='version', version='subfinder {v}'.format(v=__version__),
                        help="show subfinder's version")
    parser.add_argument('--debug',
                        action='store_true',
                        help="print debug infomation, default to False")

    args = parser.parse_args()

    # try to make `path` to unicode string in python2
    if six.PY2 and isinstance(args.path, six.binary_type):
        args.path = args.path.decode(sys.getfilesystemencoding())

    # parse config file
    args.conf = os.path.expanduser(args.conf)
    args.conf = os.path.expandvars(args.conf)
    conf_dict = {}
    if os.path.exists(args.conf):
        with open(args.conf, 'r') as fp:
            try:
                conf_dict = json.load(fp)
            except json.JSONDecodeError as e:
                print("解析配置出错，请检查配置文件格式是否正确")
                sys.exit(127)
    # parse opt `method`
    if 'method' in conf_dict:
        method = conf_dict['method']
        new_method = [find_method(m) for m in method]
        conf_dict['method'] = new_method

    # merge config file and options of cmd
    for opt, val in args.__dict__.items():
        # val is default value
        if val is False or val is None:
            continue
        # otherwise overwrite value in config file
        conf_dict[opt] = val

    root = conf_dict.pop('path')
    subfinder = subfinder_class(path=root,
                                subsearcher_class=conf_dict['method'] if 'method' in conf_dict else None,
                                **conf_dict)
    subfinder.start()
    subfinder.done()

    if args.pause:
        time.sleep(5)


if __name__ == '__main__':
    run(SubFinder)
