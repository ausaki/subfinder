# -*- coding: utf8 -*-
from __future__ import unicode_literals
from abc import abstractmethod, ABCMeta
import os
import re
import cgi
try:
    import urlparse
except ImportError as e:
    from urllib import parse as urlparse
import requests
from subfinder.tools.compressed_file import CompressedFile
from . import exceptions


registered_subsearchers = {}


def register_subsearcher(name, subsearcher_cls):
    """ register a subsearcher, the `name` is a key used for searching subsearchers.
    if the subsearcher named `name` already exists, then it's will overrite the old subsearcher.
    """
    if not issubclass(subsearcher_cls, BaseSubSearcher):
        raise ValueError(
            '{} is not a subclass of BaseSubSearcher'.format(subsearcher_cls))
    registered_subsearchers[name] = subsearcher_cls


def register(subsearcher_cls=None, name=None):
    def decorator(subsearcher_cls):
        if name is None:
            _name = subsearcher_cls.__name__
        else:
            _name = name
        register_subsearcher(_name, subsearcher_cls)
        return subsearcher_cls
    return decorator(subsearcher_cls) if subsearcher_cls is not None else decorator


def get_subsearcher(name, default=None):
    return registered_subsearchers.get(name, default)


def get_all_subsearchers():
    return registered_subsearchers


class BaseSubSearcher(object):
    """ The abstract class for search subtitles.

    You must implement following methods:
    - search_subs
    """
    __metaclass__ = ABCMeta

    SUPPORT_LANGUAGES = []
    SUPPORT_EXTS = []

    def __init__(self, subfinder,  **kwargs):
        """
        subfinder: SubFinder
        debug: 是否输出调试信息
        """
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        self.subfinder = subfinder

    def _debug(self, msg):
        self.subfinder.logger.debug(msg)

    @classmethod
    def _check_languages(cls, languages):
        for lang in languages:
            if lang not in cls.SUPPORT_LANGUAGES:
                raise exceptions.LanguageError(
                    '{} don\'t support "{}" language'.format(cls.__name__, lang))

    @classmethod
    def _check_exts(cls, exts):
        for ext in exts:
            if ext not in cls.SUPPORT_EXTS:
                raise exceptions.ExtError(
                    '{} don\'t support "{}" ext'.format(cls.__name__, ext))

    @classmethod
    def _join_url(cls, url, path):
        """ join absolute `url` and `path`(href)
        """
        return urlparse.urljoin(url, path)

    @classmethod
    def _get_videoname(cls, videofile):
        """parse the `videofile` and return it's basename
        """
        name = os.path.basename(videofile)
        name = os.path.splitext(name)[0]
        return name

    RE_SEASON_EPISODE = re.compile(
        r'[Ss](?P<season>\d+)\.?[Ee](?P<episode>\d+)')
    RE_RESOLUTION = re.compile(r'(?P<resolution>720[Pp]|1080[Pp]|HR)')
    RE_SOURCE = re.compile(
        r'\.(?P<source>BD|BluRay|BDrip|WEB-DL|HDrip|HDTVrip|HDTV|HD|DVDrip)\.')
    RE_AUDIO_ENC = re.compile(
        r'(?P<audio_encoding>mp3|DD5\.1|DDP5\.1|AC3\.5\.1)')
    RE_VIDEO_ENC = re.compile(r'(?P<video_encoding>x264|H.264|AVC1|H.265)')

    @classmethod
    def _parse_videoname(cls, videoname):
        """ parse videoname and return video info dict
        video info contains:
        - title, the name of video
        - sub_title, the sub_title of video
        - resolution,
        - source,
        -
        - season, defaults to 0
        - episode, defaults to 0
        """
        info = {
            'title': '',
            'season': 0,
            'episode': 0,
            'sub_title': '',
            'resolution': '',
            'source': '',
            'audio_encoding': '',
            'video_encoding': '',
        }
        last_index = 0
        m = cls.RE_SEASON_EPISODE.search(videoname)
        if m:
            info['season'] = int(m.group('season'))
            info['episode'] = int(m.group('episode'))
            s, e = m.span()
            info['title'] = videoname[0:s].strip('.')
            last_index = e

        m = cls.RE_RESOLUTION.search(videoname)
        if m:
            info['resolution'] = m.group('resolution')
            s, e = m.span()
            if info['title'] == '':
                info['title'] = videoname[0:s].strip('.')

            if info['season'] > 0 and info['episode'] > 0:
                info['sub_title'] = videoname[last_index:s].strip('.')
            last_index = e

        if info['title'] == '':
            info['title'] = videoname

        m = cls.RE_SOURCE.search(videoname)
        if m:
            info['source'] = m.group('source')

        m = cls.RE_AUDIO_ENC.search(videoname)
        if m:
            info['audio_encoding'] = m.group('audio_encoding')

        m = cls.RE_VIDEO_ENC.search(videoname)
        if m:
            info['video_encoding'] = m.group('video_encoding')
        return info

    @classmethod
    def _gen_subname(cls, videofile, language, ext, **kwargs):
        """ 生成字幕文件名
        """
        root, basename = os.path.split(videofile)
        name, _ = os.path.splitext(basename)
        subname = '{basename}.{language}.{ext}'.format(
            basename=name,
            language=language,
            ext=ext)
        return subname

    @classmethod
    def _extract(cls, compressed_file, videofile, exts):
        """ 解压字幕文件，如果无法解压，则直接返回 compressed_file。
        exts 参数用于过滤掉非字幕文件，只有文件的扩展名在 exts 中，才解压该文件。
        """
        if not CompressedFile.is_compressed_file(compressed_file):
            return [compressed_file]

        root = os.path.dirname(compressed_file)
        subs = []
        cf = CompressedFile(compressed_file)
        for name in cf.namelist():
            if cf.isdir(name):
                continue
            # make `name` to unicode string
            orig_name = CompressedFile.decode_file_name(name)
            _, ext = os.path.splitext(orig_name)
            ext = ext[1:]
            if ext not in exts:
                continue
            subname = cls._gen_subname(videofile, '', '', orig_name=orig_name)
            subpath = os.path.join(root, subname)
            cf.extract(name, subpath)
            subs.append(subpath)
        cf.close()
        return subs

    @classmethod
    def _filter_subinfo_list(cls, subinfo_list, videoinfo, languages, exts):
        """ filter subinfo list base on:
        - season
        - episode
        - languages
        - exts
        -
        return a best matched subinfo
        """
        season = videoinfo.get('season')
        episode = videoinfo.get('episode')
        resolution = videoinfo.get('resolution')
        source = videoinfo.get('source')
        video_encoding = videoinfo.get('video_encoding')
        audio_encoding = videoinfo.get('audio_encoding')

        filtered_subinfo_list_1 = []
        filtered_subinfo_list_2 = []
        filtered_subinfo_list_3 = []
        filtered_subinfo_list_4 = []
        filtered_subinfo_list_5 = []
        filtered_subinfo_list = []

        for subinfo in subinfo_list:
            title = subinfo.get('title')
            videoinfo_ = cls._parse_videoname(title)
            season_ = videoinfo_.get('season')
            episode_ = videoinfo_.get('episode')
            resolution_ = videoinfo_.get('resolution')
            source_ = videoinfo_.get('source')
            video_encoding_ = videoinfo_.get('video_encoding')
            audio_encoding_ = videoinfo_.get('audio_encoding')
            languages_ = subinfo.get('languages')
            exts_ = subinfo.get('exts')

            if (season == season_ and
                episode == episode_ and
                set(languages_).intersection(set(languages)) and
                    set(exts_).intersection(set(exts))):

                filtered_subinfo_list_1.append(subinfo)
                if resolution_ == resolution:
                    filtered_subinfo_list_2.append(subinfo)
                    if source_ == source:
                        filtered_subinfo_list_3.append(subinfo)
                        if video_encoding_ == video_encoding:
                            filtered_subinfo_list_4.append(subinfo)
                            if audio_encoding_ == audio_encoding:
                                filtered_subinfo_list_5.append(subinfo)
        if filtered_subinfo_list_5:
            filtered_subinfo_list = filtered_subinfo_list_5
        elif filtered_subinfo_list_4:
            filtered_subinfo_list = filtered_subinfo_list_4
        elif filtered_subinfo_list_3:
            filtered_subinfo_list = filtered_subinfo_list_3
        elif filtered_subinfo_list_2:
            filtered_subinfo_list = filtered_subinfo_list_2
        elif filtered_subinfo_list_1:
            filtered_subinfo_list = filtered_subinfo_list_1

        if not filtered_subinfo_list:
            return None
        # sort by download_count and rate
        sorted_subinfo_list = sorted(filtered_subinfo_list,
                                     key=lambda item: (
                                         item['rate'], item['download_count']),
                                     reverse=True)
        return sorted_subinfo_list[0]

    def _download_subs(self, download_link, videofile, referer='', sub_title=''):
        """ 下载字幕
        videofile: 视频文件路径
        sub_title: 字幕标题（文件名）
        download_link: 下载链接
        referer: referer
        """
        root = os.path.dirname(videofile)
        name, _ = os.path.splitext(os.path.basename(videofile))
        ext = ''

        headers = {
            'Referer': referer
        }
        res = self.session.get(download_link, headers=headers, stream=True)
        referer = res.url

        # 尝试从 Content-Disposition 中获取文件后缀名
        content_disposition = res.headers.get('Content-Disposition', '')
        if content_disposition:
            _, params = cgi.parse_header(content_disposition)
            filename = params.get('filename')
            if filename:
                _, ext = os.path.splitext(filename)
                ext = ext[1:]

        if ext == '':
            # 尝试从url 中获取文件后缀名
            p = urlparse.urlparse(res.url)
            path = p.path
            if path:
                _, ext = os.path.splitext(path)
                ext = ext[1:]

        if ext == '':
            # 尝试从字幕标题中获取文件后缀名
            _, ext = os.path.splitext(sub_title)
            ext = ext[1:]

        filename = '{}.{}'.format(name, ext)
        filepath = os.path.join(root, filename)
        with open(filepath, 'wb') as fp:
            for chunk in res.iter_content(8192):
                fp.write(chunk)

        return filepath, referer

    def _search_subs(self, videofile, languages, exts):
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
                'ext': '',      # ext
                'subname': '',  # the filename of subtitles
                'downloaded': False, # it's tell `SubFinder` whether need to download.
            },
            {
                'link': '',
                'language': '',
                'ext': '',
                'subname': '',
            },
            ...
        ]
        - `link`, it's optional, but if `downloaded` is False, then `link` is required.
        - `language`, it's optional
        - `subname`, it's optional, but if `downloaded` is False, then `subname` is required.
        - `downloaded`, `downloaded` is required.
            if `downloaded` is True, then `SubFinder` will not download again,
            otherwise `SubFinder` will download link.

        sub-class should implement this private method.
        """
        return []

    def search_subs(self, videofile, languages=None, exts=None):
        if languages is None:
            languages = self.SUPPORT_LANGUAGES
        elif isinstance(languages, str):
            languages = [languages]
        self._check_languages(languages)

        if exts is None:
            exts = self.SUPPORT_EXTS
        elif isinstance(exts, str):
            exts = [exts]
        self._check_exts(exts)

        return self._search_subs(videofile, languages, exts)

    def __str__(self):
        if hasattr(self.__class__, 'shortname'):
            name = self.__class__.shortname
        else:
            name = self.__class__.__name__
        return '<{}>'.format(name)

    def __unicode__(self):
        return self.__str__()
