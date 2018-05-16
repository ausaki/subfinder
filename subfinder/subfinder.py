# -*- coding: utf8 -*-

from gevent import monkey
monkey.patch_all()
import os
import sys
import logging
import hashlib
import mimetypes
import argparse
import random
import time
import json
import sqlite3
from abc import abstractmethod, ABCMeta
from gevent.pool import Pool
import requests
from . import exceptions


class BaseSubSearcher(object):
    """ The abstract class for search subtitles.

    You must implement following methods:
    - search_subs
    """
    __metaclass__ = ABCMeta

    SUPPORT_LANGUAGES = []
    SUPPORT_EXTS = []

    @abstractmethod
    def search_subs(self, videofile, languages, exts, *args, **kwargs):
        """ search subtitles of videofile.

        `videofile` is the absolute(or relative) path of the video file.

        `languages` is the language of subtitle, e.g chn, eng, the support for language is difference, depende on
        implemention of subclass. `languages` accepts one language or a list of language

        `exts` is the format of subtitle, e.g ass, srt, sub, idx, the support for ext is difference,
        depende on implemention of subclass. `ext` accepts one ext or a list of ext

        return a list of subtitle info
        [
            {
                'link': '',     # download link
                'language': '', # language
                'format': '',   # format
                'subname': '',  # the filename of subtitles
            },
            {
                'link': '',
                'language': '',
                'format': '',
                'subname': '',
            },
            ...
        ] 
        """
        pass

    def _check_languages(self, languages):
        for lang in languages:
            if lang not in self.SUPPORT_LANGUAGES:
                raise exceptions.LanguageError(
                    '{} don\'t support {} language'.format(self.__class__.__name__, lang))

    def _check_exts(self, exts):
        for ext in exts:
            if ext not in self.SUPPORT_EXTS:
                raise exceptions.ExtError(
                    '{} don\'t support {} ext'.format(self.__class__.__name__, lang))


class ShooterSubSearcher(BaseSubSearcher):
    """ find subtitles from shooter.org
    API URL: https://www.shooter.cn/api/subapi.php
    """

    API_URL = 'https://www.shooter.cn/api/subapi.php'
    SUPPORT_LANGUAGES = ['Chn', 'Eng']
    SUPPORT_EXTS = ['ass', 'srt']

    def __init__(self, *args, **kwargs):
        super(ShooterSubSearcher, self).__init__(*args, **kwargs)
        self.session = requests.Session()

    def search_subs(self, videofile, languages=None, exts=None):
        """
        language supports following format:
        - "Eng"
        - "Chn"
        `languages` default to ["Chn"]
        """
        videofile = os.path.abspath(videofile)
        if languages is None:
            languages = [self.SUPPORT_LANGUAGES[0]]
        elif isinstance(languages, str):
            languages = [languages]
        self._check_languages(languages)

        if exts is None:
            exts = self.SUPPORT_EXTS
        elif isinstance(exts, str):
            exts = [exts]
        self._check_exts(exts)

        filehash = self._compute_video_hash(videofile)
        root, basename = os.path.split(videofile)
        payload = {'filehash': filehash,
                   'pathinfo': basename,
                   'format': 'json',
                   'lang': ''}

        result = {}
        for language in languages:
            payload['lang'] = language
            try:
                res = self.session.post(self.API_URL, data=payload)
                result[language] = res.json()
            except Exception as e:
                raise exceptions.SearchingSubinfoError(str(e))

        subinfos = []
        for language, subinfolist in result.items():
            ext_set = set()
            for subinfo in subinfolist:
                desc = subinfo['Desc']
                delay = subinfo['Delay']
                files = subinfo['Files']
                for item in files:
                    ext_ = item['Ext']
                    ext_ = ext_.lower()
                    link = item['Link']
                    if ext_ in exts and ext_ not in ext_set:
                        subinfos.append({
                            'link': link,
                            'language': language,
                            'subname': self._gen_subname(videofile, language, ext_),
                            'ext': ext_
                        })
                        ext_set.add(ext_)
        return subinfos

    def _gen_subname(self, videofile, language, ext):
        """ generate filename of subtitles
        :TODO: fix the conflict of subname
        """
        root, basename = os.path.split(videofile)
        name, _ = os.path.splitext(basename)
        subname = '{basename}.{language}.{ext}'.format(
            basename=name,
            language=language,
            ext=ext)
        p = os.path.join(root, subname)
        return p

    def _compute_video_hash(self, videofile):
        """ compute videofile's hash
        reference: https://docs.google.com/document/d/1w5MCBO61rKQ6hI5m9laJLWse__yTYdRugpVyz4RzrmM/preview
        """
        seek_positions = [None] * 4
        hash_result = []
        with open(videofile, 'rb') as fp:
            total_size = os.fstat(fp.fileno()).st_size
            if total_size < 8192 + 4096:
                raise exceptions.InvalidFileError(
                    'the video[{}] is too small'.format(os.path.basename(videofile)))

            seek_positions[0] = 4096
            seek_positions[1] = total_size // 3 * 2
            seek_positions[2] = total_size // 3
            seek_positions[3] = total_size - 8192
            for pos in seek_positions:
                fp.seek(pos, 0)
                data = fp.read(4096)
                m = hashlib.md5(data)
                hash_result.append(m.hexdigest())
        return ';'.join(hash_result)


class SubFinder(object):
    """ find subtitles and download subtitles
    """

    VIDEO_EXTS = ['.mkv', '.mp4', '.ts', '.avi', '.wmv']

    def __init__(self, path='./', languages=None, exts=None, subsearcher_class=None, **kwargs):
        self.set_path(path)
        self.languages = languages
        self.exts = exts

        if subsearcher_class is None:
            subsearcher_class = ShooterSubSearcher
        self.subsearcher = subsearcher_class()

        # silence: dont print anything
        self.silence = kwargs.get('silence', False)
        # logger's output
        self.logger_output = kwargs.get('logger_output', sys.stdout)

        self._init_session()
        self._init_gevent_pool()
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

    def _init_gevent_pool(self):
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

    def _save_history(self):
        """ save downloading history to .subfinder_history.db(sqlite3)
        """
        root = ''
        if os.path.isfile(self.path):
            root = os.path.dirname(self.path)
        else:
            root = self.path
        dbname = '.subfinder_history.db'
        conn = sqlite3.connect(os.path.join(root, dbname))
        cursor = conn.cursor()
        # create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                create_at INTEGER,
                content TEXT)
        ''')
        content = json.dumps(self._history)
        cursor.execute('INSERT INTO history(create_at, content) VALUES(?, ?)',
                       (int(time.time()), content))
        conn.commit()
        cursor.close()
        conn.close()

    def _download(self, videofile):
        basename = os.path.basename(videofile)
        self.logger.info('Start search subtitles of {}'.format(basename))
        try:
            subinfos = self.subsearcher.search_subs(
                videofile, self.languages, self.exts)
        except exceptions.SearchingSubinfoError as e:
            self.logger.error(
                'search subinfo of {} happening error: {}'.format(basename, str(e)))
            return
        except exceptions.InvalidFileError as e:
            self.logger.error(str(e))
            return
        except Exception as e:
            self.logger.error(e)
            return

        self.logger.info('Find {} subtitles for {}, prepare to download'.format(
            len(subinfos), basename))
        try:
            for subinfo in subinfos:
                link = subinfo['link']
                language = subinfo['language']
                ext = subinfo['ext']
                subname = subinfo.get('subname')
                res = self.session.get(link, stream=True)
                with open(subname, 'wb') as fp:
                    for chunk in res.iter_content(8192):
                        fp.write(chunk)
                self._history[videofile].append(subname)

            self.logger.info('Downloaded {} subtitles for {}'.format(
                len(subinfos),
                basename))
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
        self._save_history()
        self.logger.info('Done! enjoying the movies!')

    def done(self):
        self.recovery_stderr()

    def remove_subtitles(self):
        pass


def find_method(m):
    g = globals()
    method = g.get(m)
    return method


def main():
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

    subfinder = SubFinder(path=args.path,
                          languages=args.languages,
                          exts=args.exts,
                          subsearcher_class=args.method,
                          silence=args.silence)
    subfinder.start()
    subfinder.done()


if __name__ == '__main__':
    main()
