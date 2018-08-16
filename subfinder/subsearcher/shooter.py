from __future__ import unicode_literals
import os
import hashlib
import requests
from .subsearcher import BaseSubSearcher
from . import exceptions

class ShooterSubSearcher(BaseSubSearcher):
    """ find subtitles from shooter.org
    API URL: https://www.shooter.cn/api/subapi.php
    """
    shortname = 'shooter'
    API_URL = 'https://www.shooter.cn/api/subapi.php'
    SUPPORT_LANGUAGES = ['zh', 'en']
    SUPPORT_EXTS = ['ass', 'srt']

    SHOOTER_LANGUAGES_MAP = {
        'zh': 'Chn',
        'en': 'Eng'
    }

    def _search_subs(self, videofile, languages, exts):
        filehash = self._compute_video_hash(videofile)
        root, basename = os.path.split(videofile)
        payload = {'filehash': filehash,
                   'pathinfo': basename,
                   'format': 'json',
                   'lang': ''}

        result = {}
        for language in languages:
            payload['lang'] = self.SHOOTER_LANGUAGES_MAP.get(language)
            res = self.session.post(self.API_URL, data=payload)
            if res.status_code == requests.codes.ok:
                try:
                    result[language] = res.json()
                except Exception as e:
                    result[language] = []

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
                            'ext': ext_,
                            'downloaded': False
                        })
                        ext_set.add(ext_)
        return subinfos

    @staticmethod
    def _gen_subname(videofile, language, ext):
        """ generate filename of subtitles
        :TODO: fix the conflict of subname
        """
        root, basename = os.path.split(videofile)
        name, _ = os.path.splitext(basename)
        subname = '{basename}.{language}.{ext}'.format(
            basename=name,
            language=language,
            ext=ext)
        return subname

    @staticmethod
    def _compute_video_hash(videofile):
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