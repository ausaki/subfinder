# -*- coding: utf8 -*-
import os
import hashlib
from abc import abstractmethod, ABCMeta
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