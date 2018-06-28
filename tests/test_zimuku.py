#! /usr/bin/env python
# -*- coding: utf -*-

from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subsearcher.zimuku import ZimukuSubSearcher
from subfinder.subsearcher.exceptions import LanguageError, ExtError


@pytest.fixture(scope='module')
def zimuku():
    z = ZimukuSubSearcher()
    return z


class TestZimukuSubSearcher:

    def test_languages(self, zimuku):
        zimuku._check_languages(['zh_chs'])
        with pytest.raises(LanguageError):
            zimuku._check_languages(['Lang'])

    def test_exts(self, zimuku):
        zimuku._check_exts(['ass'])
        with pytest.raises(ExtError):
            zimuku._check_exts(['Ext'])
    
    def test_parse_videoname(self, zimuku):
        test_cases = {
            'TV_TITLE.720p.HDTV.x264-AVS': {
                'title': 'TV_TITLE.720p.HDTV.x264-AVS',
                'season': 0,
                'episode': 0,
                'sub_title': '',
                'resolution': '720p',
                'source': 'HDTV',
                'video_encoding': 'x264',
                'audio_encoding': ''
            },
            'TV_TITLE.S01E01.SUB_TITLE.720p.HDTV.AC3.5.1.x264-AVS': {
                'title': 'TV_TITLE',
                'season': 1,
                'episode': 1,
                'sub_title': 'SUB_TITLE',
                'resolution': '720p',
                'source': 'HDTV',
                'video_encoding': 'x264',
                'audio_encoding': 'AC3.5.1'
            },
            'TV_TITLE.S10E10.SUB_TITLE.1080P.WEB-DL.AC3.5.1.x264-AVS': {
                'title': 'TV_TITLE',
                'season': 10,
                'episode': 10,
                'sub_title': 'SUB_TITLE',
                'resolution': '1080P',
                'source': 'WEB-DL',
                'video_encoding': 'x264',
                'audio_encoding': 'AC3.5.1'
            },
        }
        for name, info in test_cases.items():
            info_ = zimuku._parse_videoname(name)
            assert info == info_
    
    def test_parse_download_count(self, zimuku):
        test_cases = {
            '100': 100,
            '1千': 1000,
            '10千': 10000,
            '5万': 50000,
            '2百万': 2000000
        }
        for text, count in test_cases.items():
            c = zimuku._parse_downloadcount(text)
            assert c == count
