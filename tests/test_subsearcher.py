#! /usr/bin/env python
# -*- coding: utf -*-
from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subsearcher import BaseSubSearcher
from subfinder.subsearcher.exceptions import LanguageError, ExtError


def test_languages():
    with pytest.raises(LanguageError):
        BaseSubSearcher._check_languages(['Lang'])


def test_exts():
    with pytest.raises(ExtError):
        BaseSubSearcher._check_exts(['Ext'])


def test_parse_videoname():
    test_cases = {
        'TV_TITLE.720p.HDTV.x264-AVS': {
            'title': 'TV_TITLE',
            'season': 0,
            'episode': 0,
            'resolution': '720p',
            'source': 'HDTV',
            'video_encoding': 'x264',
            'audio_encoding': ''
        },
        'TV_TITLE.S01E01.SUB_TITLE.720p.HDTV.AC3.5.1.x264-AVS': {
            'title': 'TV_TITLE',
            'season': 1,
            'episode': 1,
            'resolution': '720p',
            'source': 'HDTV',
            'video_encoding': 'x264',
            'audio_encoding': 'AC3.5.1'
        },
        'TV_TITLE.S10E10.SUB_TITLE.1080P.WEB-DL.AC3.5.1.x264-AVS': {
            'title': 'TV_TITLE',
            'season': 10,
            'episode': 10,
            'resolution': '1080P',
            'source': 'WEB-DL',
            'video_encoding': 'x264',
            'audio_encoding': 'AC3.5.1'
        },
        'Ballon.2018.Bluray.REMUX.GER.2160p.HEVC.TrueHD.7.1.Atmos-MOLAMOLA.mkv': {
            'title': 'Ballon.2018',
            'season': 0,
            'episode': 0,
            'resolution': '2160p',
            'source': 'Bluray',
            'video_encoding': '',
            'audio_encoding': ''
        }
    }
    for name, info in test_cases.items():
        info_ = BaseSubSearcher._parse_videoname(name)
        assert info == info_

def test_gen_subname():
    vidoefile = 'test.mkv'
    language = 'zh'
    ext = 'srt'
    subname = BaseSubSearcher._gen_subname(vidoefile, language, ext)
    assert subname == 'test.zh.srt'
