# -*- coding: utf8 -*-
from __future__ import unicode_literals
import os
import sys
import logging
import mimetypes
import time
import json
import sqlite3
import requests
from .subsearcher import get_subsearcher, exceptions


class Pool(object):
    def __init__(self, size):
        self.size = size

    def spawn(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

    def join(self):
        return


class SubFinder(object):
    """ find subtitles and download subtitles
    """

    VIDEO_EXTS = ['.mkv', '.mp4', '.ts', '.avi', '.wmv']

    def __init__(self, path='./', languages=None, exts=None, subsearcher_class=None, **kwargs):
        self.set_path(path)
        self.languages = languages
        self.exts = exts

        if subsearcher_class is None:
            subsearcher_class = get_subsearcher('default')
        if not isinstance(subsearcher_class, list):
            subsearcher_class = [subsearcher_class]
        
        self.subsearcher = [sc() for sc in subsearcher_class]

        # silence: dont print anything
        self.silence = kwargs.get('silence', False)
        # logger's output
        self.logger_output = kwargs.get('logger_output', sys.stdout)

        self._init_session()
        self._init_pool()
        self._init_logger()

        # _history: recoding downloading history
        self._history = {}


    def _is_videofile(self, f):
        """ determine `f` is a valid video file
        """
        if os.path.isfile(f):
            types = mimetypes.guess_type(f)
            mtype = types[0]
            if (mtype and mtype.split('/')[0] == 'video') or (os.path.splitext(f)[1] in self.VIDEO_EXTS):
                return True
        return False

    def _filter_path(self, path):
        """ filter path recursively, return a list of videofile
        """
        if self._is_videofile(path):
            return [path, ]

        if os.path.isdir(path):
            result = []
            for root, dirs, files in os.walk(path):
                result.extend(filter(self._is_videofile, map(
                    lambda f: os.path.join(root, f), files)))
            return result
        else:
            return []

    def _init_session(self):
        """ init request session, for download subtitles
        """
        self.session = requests.Session()
        self.session.mount('http://', adapter=requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=100))

    def _init_pool(self):
        self.pool = Pool(10)

    def _init_logger(self):
        self._devnull = open(os.devnull, 'w')
        self._old_stderr = sys.stderr

        if self.silence:
            sys.stderr = self._devnull

        self.logger = logging.getLogger('SubFinder')
        self.logger.handlers = []
        self.logger.setLevel(logging.DEBUG)
        s = self.logger_output
        if self.silence:
            s = self._devnull
        sh = logging.StreamHandler(stream=s)
        sh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '[%(asctime)s]-[%(levelname)s]: %(message)s', datefmt='%m/%d %H:%M:%S')
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

    def recovery_stderr(self):
        self._devnull.close()
        sys.stderr = self._old_stderr

    def _download(self, videofile):
        basename = os.path.basename(videofile)

        subinfos = []
        for subsearcher in self.subsearcher:
            self.logger.info('Start search subtitles of {} by {}'.format(basename, subsearcher))
            try:
                subinfos = subsearcher.search_subs(
                    videofile, self.languages, self.exts)
            except Exception as e:
                self.logger.error(
                    'search subinfo of {} happening error: {}'.format(basename, str(e)))
                continue
            if subinfos:
                break                
        self.logger.info('Find {} subtitles for {}, prepare to download'.format(
            len(subinfos), basename))
        try:
            for subinfo in subinfos:
                downloaded = subinfo.get('downloaded', False)
                if downloaded:
                    if isinstance(subinfo['subname'], (list, tuple)):
                        self._history[videofile].extend(subinfo['subname'])
                    else:
                        self._history[videofile].append(subinfo['subname'])
                else:
                    link = subinfo.get('link')
                    subname = subinfo.get('subname')
                    subpath = os.path.join(os.path.dirname(videofile), subname)
                    res = self.session.get(link, stream=True)
                    with open(subpath, 'wb') as fp:
                        for chunk in res.iter_content(8192):
                            fp.write(chunk)
                    self._history[videofile].append(subpath)
        except Exception as e:
            self.logger.error(str(e))

    def set_path(self, path):
        path = os.path.abspath(path)
        self.path = path

    def start(self):
        self.logger.info('Start')
        videofiles = self._filter_path(self.path)
        l = len(videofiles)
        if l == 0:
            self.logger.info(
                "Doesn't find any video files in {}".format(self.path))
            return
        else:
            self.logger.info('Find {} video files'.format(l))

        for f in videofiles:
            self._history[f] = []
            self.pool.spawn(self._download, f)
        self.pool.join()
        self.logger.info('='*20 + 'Done! enjoying the movies!' + '='*20)
        for v, subs in self._history.items():
            basename = os.path.basename(v)
            self.logger.info('{}: find {} subtitles'.format(basename, len(subs)))

    def done(self):
        self.recovery_stderr()
