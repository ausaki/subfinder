# -*- coding: utf8 -*-
from __future__ import unicode_literals
import os
import sys
import logging
import mimetypes
import traceback
import requests
from .subsearcher import get_subsearcher, exceptions


class Pool(object):
    """ 模拟线程池，实际上还是同步执行代码
    """
    def __init__(self, size):
        self.size = size

    def spawn(self, fn, *args, **kwargs):
        fn(*args, **kwargs)

    def join(self):
        return


class SubFinder(object):
    """ 字幕查找器
    """

    VIDEO_EXTS = ['.mkv', '.mp4', '.ts', '.avi', '.wmv']

    def __init__(self, path='./', languages=None, exts=None, subsearcher_class=None, **kwargs):
        self.set_path(path)
        self.languages = languages
        self.exts = exts

        # silence: dont print anything
        self.silence = kwargs.get('silence', False)
        # logger's output
        self.logger_output = kwargs.get('logger_output', sys.stdout)
        # debug
        self.debug = kwargs.get('debug', False)
        self._init_session()
        self._init_pool()
        self._init_logger()

        # _history: recoding downloading history
        self._history = {}

        if subsearcher_class is None:
            subsearcher_class = get_subsearcher('default')
        if not isinstance(subsearcher_class, list):
            subsearcher_class = [subsearcher_class]

        self.subsearcher = [sc(self) for sc in subsearcher_class]

    def _is_videofile(self, f):
        """ 判断 f 是否是视频文件
        """
        if os.path.isfile(f):
            types = mimetypes.guess_type(f)
            mtype = types[0]
            if (mtype and mtype.split('/')[0] == 'video') or (os.path.splitext(f)[1] in self.VIDEO_EXTS):
                return True
        return False

    def _filter_path(self, path):
        """ 筛选出 path 目录下所有的视频文件
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
        """ 初始化 requests.Session
        """
        self.session = requests.Session()
        self.session.mount('http://', adapter=requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=100))

    def _init_pool(self):
        self.pool = Pool(10)

    def _init_logger(self):
        log_level = logging.INFO
        if self.silence:
            log_level = logging.CRITICAL + 1
        if self.debug:
            log_level = logging.DEBUG
        self.logger = logging.getLogger('SubFinder')
        self.logger.handlers = []
        self.logger.setLevel(log_level)
        sh = logging.StreamHandler(stream=self.logger_output)
        sh.setLevel(log_level)
        formatter = logging.Formatter(
            '[%(asctime)s]-[%(levelname)s]: %(message)s', datefmt='%m/%d %H:%M:%S')
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

    def _download(self, videofile):
        """ 调用 SubSearcher 搜索并下载字幕
        """
        basename = os.path.basename(videofile)

        subinfos = []
        for subsearcher in self.subsearcher:
            self.logger.info(
                '{0}：开始使用 {1} 搜索字幕'.format(basename, subsearcher))
            try:
                subinfos = subsearcher.search_subs(
                    videofile, self.languages, self.exts)
            except Exception as e:
                err = str(e)
                if self.debug:
                    err = traceback.format_exc()
                self.logger.error(
                    '{}：搜索字幕发生错误： {}'.format(basename, err))
                continue
            if subinfos:
                break
        self.logger.info('{1}：找到 {0} 个字幕, 准备下载'.format(
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
        """ SubFinder 入口，开始函数
        """
        self.logger.info('开始')
        videofiles = self._filter_path(self.path)
        l = len(videofiles)
        if l == 0:
            self.logger.info(
                '在 {} 下没有发现视频文件'.format(self.path))
            return
        else:
            self.logger.info('找到 {} 个视频文件'.format(l))

        for f in videofiles:
            self._history[f] = []
            self.pool.spawn(self._download, f)
        self.pool.join()
        self.logger.info('='*20 + '下载完成' + '='*20)
        for v, subs in self._history.items():
            basename = os.path.basename(v)
            self.logger.info(
                '{}: 下载 {} 个字幕'.format(basename, len(subs)))

    def done(self):
       pass
