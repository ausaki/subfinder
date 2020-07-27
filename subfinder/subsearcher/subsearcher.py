# -*- coding: utf8 -*-
from __future__ import unicode_literals
from abc import abstractmethod, ABCMeta
import os
from os.path import join
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
    shortname = 'base_subsearcher'
    API_URL = ''

    def __init__(self, subfinder,  api_urls=None, **kwargs):
        """
        subfinder: SubFinder
        api_urls: api_urls
        """
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        self.subfinder = subfinder
        self.api_urls = api_urls if api_urls else {}
        self.API_URL = self.api_urls.get(self.shortname, self.__class__.API_URL)

        self.languages = ''
        self.exts = ''
        self.videofile = ''
        self.videoname = ''
        self.videoinfo = {}
        self.keywords = []
        self.referer = ''

    def _debug(self, msg):
        self.subfinder.logger.debug(msg)

    @classmethod
    def _check_languages(cls, languages):
        for lang in languages:
            if lang not in cls.SUPPORT_LANGUAGES:
                raise exceptions.LanguageError(
                    '{} doesn\'t support "{}" language'.format(cls.__name__, lang))

    @classmethod
    def _check_exts(cls, exts):
        for ext in exts:
            if ext not in cls.SUPPORT_EXTS:
                raise exceptions.ExtError(
                    '{} doesn\'t support "{}" ext'.format(cls.__name__, ext))

    @classmethod
    def _join_url(cls, url, path):
        """ join absolute `url` and `path`(href)
        """
        return urlparse.urljoin(url, path)

    @abstractmethod
    def search_subs(self, videofile, languages=None, exts=None, keyword=None):
        """ search subtitles of videofile.

        `videofile` is the absolute(or relative) path of the video file.

        `languages` is the language of subtitle, e.g chn, eng, the support for language is difference, depende on
        implemention of subclass. `languages` accepts one language or a list of language

        `exts` is the format of subtitle, e.g ass, srt, sub, idx, the support for ext is difference,
        depende on implemention of subclass. `ext` accepts one ext or a list of ext

        `keyword` is used to searching on the subtitle website.

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
        """
        pass

    def __str__(self):
        if hasattr(self.__class__, 'shortname'):
            name = self.__class__.shortname
        else:
            name = self.__class__.__name__
        return '<{}>'.format(name)

    def __unicode__(self):
        return self.__str__()


class HTMLSubSearcher(BaseSubSearcher):
    __metaclass__ = ABCMeta

    LANGUAGES_MAP = {
        '简体': 'zh_chs',
        '繁體': 'zh_cht',
        'English': 'en',
        'english': 'en',
        '英文': 'en',
        '双语': 'zh_en',
        '中英': 'zh_en',
    }
    COMMON_LANGUAGES = ['简体', '繁体', '英文']
    shortname = 'html_subsearcher'

    @classmethod
    def _get_videoname(cls, videofile):
        """parse the `videofile` and return it's basename
        """
        name = os.path.basename(videofile)
        name = os.path.splitext(name)[0]
        return name

    RE_SEASON = re.compile(
        r'[Ss](?P<season>\d+)\.?')
    RE_SEASON_EPISODE = re.compile(
        r'[Ss](?P<season>\d+)\.?[Ee](?P<episode>\d+)')
    RE_RESOLUTION = re.compile(r'(?P<resolution>720[Pp]|1080[Pp]|2160[Pp]|HR)')
    RE_SOURCE = re.compile(
        r'\.(?P<source>BD|Blu[Rr]ay|BDrip|WEB-DL|HDrip|HDTVrip|HDTV|HD|DVDrip)\.')
    RE_AUDIO_ENC = re.compile(
        r'(?P<audio_encoding>mp3|DD5\.1|DDP5\.1|AC3\.5\.1)')
    RE_VIDEO_ENC = re.compile(r'(?P<video_encoding>x264|H\.264|AVC1|H\.265)')

    @classmethod
    def _parse_videoname(cls, videoname):
        """ parse videoname and return video info dict
        video info contains:
        - title, the name of video
        - sub_title, the sub_title of video
        - resolution,
        - source,
        - season, defaults to 0
        - episode, defaults to 0
        """
        info = VideoInfo()
        mapping = {
            'resolution': cls.RE_RESOLUTION,
            'source': cls.RE_SOURCE,
            'audio_encoding': cls.RE_AUDIO_ENC,
            'video_encoding': cls.RE_VIDEO_ENC
        }
        index = len(videoname)
        m = cls.RE_SEASON_EPISODE.search(videoname)
        if m:
            info['season'] = int(m.group('season'))
            info['episode'] = int(m.group('episode'))
            index, _ = m.span()
            info['title'] = videoname[0:index].strip('.')
        else:
            m = cls.RE_SEASON.search(videoname)
            if m:
                info['season'] = int(m.group('season'))
                index, _ = m.span()
                info['title'] = videoname[0:index].strip('.')

        for k, r in mapping.items():
            m = r.search(videoname)
            if m:
                info[k] = m.group(k)
                i, e = m.span()
                if info['title'] == '' or i < index:
                    index = i
                    info['title'] = videoname[0:index].strip('.')

        if info['title'] == '':
            i = videoname.find('.')
            info['title'] = videoname[:i] if i > 0 else videoname

        return info

    def _gen_subname(self, origin_file, language=None, ext=None):
        if not language:
            language_ = []
            try:
                for l in self.COMMON_LANGUAGES:
                    if origin_file.find(l) >= 0:
                        language_.append(l)
            except Exception:
                pass
            language = '&'.join(language_)
        if language and not language.startswith('.'):
            language = '.' + language

        basename = os.path.basename(self.videofile)
        basename, _ = os.path.splitext(basename)
        if not ext:
            _, ext = os.path.splitext(origin_file)
        if not ext.startswith('.'):
            ext = '.' + ext

        return '{basename}{language}{ext}'.format(basename=basename, language=language, ext=ext)

    def _extract(self, compressed_file):
        """ 解压字幕文件，如果无法解压，则直接返回 compressed_file。
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
            origin_file = CompressedFile.decode_file_name(name)
            _, ext = os.path.splitext(origin_file)
            ext = ext[1:]
            if self.exts and ext not in self.exts:
                continue
            subname = self._gen_subname(origin_file)
            subpath = os.path.join(root, subname)
            cf.extract(name, subpath)
            subs.append(subpath)
        cf.close()
        return subs

    def _download_subtitle(self, download_link, subtitle):
        """ 下载字幕
        videofile: 视频文件路径
        sub_title: 字幕标题（文件名）
        download_link: 下载链接
        """
        root = os.path.dirname(self.videofile)
        name = self.videoname
        ext = ''
        res = self.session.get(download_link, headers={'Referer': self.referer}, stream=True)
        self.referer = res.url
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
            _, ext = os.path.splitext(subtitle)
            ext = ext[1:]

        filename = '{}.{}'.format(name, ext)
        filepath = os.path.join(root, filename)
        with open(filepath, 'wb') as fp:
            for chunk in res.iter_content(8192):
                fp.write(chunk)
        res.close()
        return filepath

    @classmethod
    def _gen_keyword(cls, videoinfo):
        """ 获取关键词
        """
        separators = ['.', ' ']
        keywords = []
        for sep in separators:
            keyword = [videoinfo.get('title')]
            if videoinfo['season'] != 0:
                keyword.append('S{:02d}'.format(videoinfo['season']))
            if videoinfo['episode'] != 0:
                keyword.append('E{:02d}'.format(videoinfo['episode']))
            # replace space with ''
            keyword_str = sep.join(keyword)
            keyword_str = re.sub(r'\s+', ' ', keyword_str)
            keywords.append(keyword_str)
        return keywords

    def _filter_subinfo_list(self, subinfo_list):
        """ filter subinfo list base on:
        - season
        - episode
        - languages
        - exts
        -
        return a best matched subinfo
        """
        filter_field_list = [
            'season',
            'episode',
            'resolution',
            'source',
            'video_encoding',
            'audio_encoding'
        ]
        videoinfo = self.videoinfo
        filtered_subinfo_list = dict((f, []) for f in filter_field_list)
        languages = set(self.languages)
        exts = set(self.exts)
        for subinfo in subinfo_list:
            languages_ = subinfo.get('languages')
            exts_ = subinfo.get('exts')
            if languages_ and not (languages & set(languages_)):
                continue
            if exts_ and not (exts & set(exts_)):
                continue
            title = subinfo.get('title')
            videoinfo_ = self._parse_videoname(title)
            last_field = None
            for field in filter_field_list:
                i = videoinfo.get(field)
                if isinstance(i, str):
                    i = i.lower()
                j = videoinfo_.get(field)
                if isinstance(j, str):
                    j = j.lower()
                if i == j:
                    last_field = field
                else:
                    break
            if last_field is not None and last_field != filter_field_list[0]:
                filtered_subinfo_list[last_field].append(subinfo)
        for field in reversed(filter_field_list):
            if len(filtered_subinfo_list[field]) > 0:
                # sort by download_count and rate
                sorted_subinfo_list = sorted(filtered_subinfo_list[field],
                                             key=lambda item: (item['rate'], item['download_count']), reverse=True)
                return sorted_subinfo_list[0]

    @abstractmethod
    def _get_subinfo_list(self, keyword):
        """ return subinfo_list of videoname
        """
        # searching subtitles
        pass

    @abstractmethod
    def _visit_detailpage(self, detailpage_link):
        pass

    @abstractmethod
    def _visit_downloadpage(self, downloadpage_link):
        """ get the real download link of subtitles.
        """
        pass

    def _prepare_search_subs(self, videofile, languages=None, exts=None, keyword=None):
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

        self.languages = languages
        self.exts = exts
        self.videofile = videofile
        self.videoname = self._get_videoname(videofile)  # basename, not include ext
        self.videoinfo = self._parse_videoname(self.videoname)
        if keyword is None:
            keywords = self._gen_keyword(self.videoinfo)
        else:
            keywords = [keyword]
        self.keywords = keywords
    
    def search_subs(self, videofile, languages=None, exts=None, keyword=None):
        self._prepare_search_subs(videofile, languages, exts, keyword)
        self._debug('keywords: {}'.format(self.keywords))
        self._debug('videoinfo: {}'.format(self.videoinfo))
        subinfo = self._get_subinfo()
        if not subinfo:
            return []
        subs = self._download_subs(subinfo)
        return [{
            'link': self.referer,
            'language': subinfo['languages'],
            'ext': subinfo['exts'],
            'subname': subs,
            'downloaded': True
        }] if subs else []

    def _get_subinfo(self):
        subinfo = None
        for keyword in self.keywords:
            subinfo_list = self._get_subinfo_list(keyword)
            self._debug('subinfo_list: {}'.format(subinfo_list))
            subinfo = self._filter_subinfo_list(subinfo_list)
            self._debug('subinfo: {}'.format(subinfo))
            if subinfo:
                break
        return subinfo

    def _download_subs(self, subinfo):
        downloadpage_link = self._visit_detailpage(subinfo['link'])
        self._debug('downloadpage_link: {}'.format(downloadpage_link))
        subtitle_download_link = self._visit_downloadpage(downloadpage_link)
        self._debug('subtitle_download_link: {}'.format(subtitle_download_link))
        filepath = self._download_subtitle(subtitle_download_link, subinfo['title'])
        self._debug('filepath: {}'.format(filepath))
        subs = self._extract(filepath)
        self._debug('subs: {}'.format(subs))
        return subs


class VideoInfo(dict):
    FIELDS = [
        'title',
        'season',
        'episode',
        'resolution',
        'source',
        'audio_encoding',
        'video_encoding',
    ]

    def __init__(self, *args, **kwargs) -> None:
        super(VideoInfo, self).__init__(*args, **kwargs)
        self['title'] = ''
        self['season'] = 0
        self['episode'] = 0
        self['resolution'] = ''
        self['source'] = ''
        self['audio_encoding'] = ''
        self['video_encoding'] = ''
        for k, v in kwargs:
            if k in self.FIELDS:
                self[k] = v


class SubInfo(dict):
    FIELDS = [
        'title',
        'link',
        'author',
        'exts',
        'languages',
        'rate',
        'download_count',
    ]

    def __init__(self, *args, **kwargs) -> None:
        super(SubInfo, self).__init__(*args, **kwargs)
        self['title'] = ''
        self['link'] = ''
        self['author'] = ''
        self['exts'] = []
        self['languages'] = []
        self['rate'] = 0
        self['download_count'] = 0

        for k, v in kwargs:
            if k in self.FIELDS:
                self[k] = v
