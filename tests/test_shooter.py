#! /usr/bin/env python

from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subsearcher import ShooterSubSearcher
from subfinder.subfinder import SubFinder
from subfinder.subsearcher.exceptions import LanguageError, ExtError, ShooterAPIError


@pytest.fixture(scope='module')
def shooter():
    s = ShooterSubSearcher(SubFinder())
    return s


RIGHT_HASH = ('54b690dcdbd19e9675042612b9c25143;'
    '48d6d334d0c51066f39f09f796c4bebd;'
    'd422f9797befa81a0c2ae880b6ceaa34;'
    'fddfb48e1bdd219fad1ae5ab2c4c01ed')

VIDEOFILE = os.path.expanduser('~/Downloads/subfinder_test/Marvels.Agents.of.S.H.I.E.L.D.S05E21.720p.HDTV.x264-AVS.mkv')

def test_compute_videohash(shooter):
    if not os.path.exists(VIDEOFILE):
        pytest.skip('test video file not exists')
    else:
        h = shooter._compute_video_hash(VIDEOFILE)
        assert h == RIGHT_HASH


def test_languages(shooter):
    shooter._check_languages(['zh'])
    with pytest.raises(LanguageError):
        shooter._check_languages(['Lang'])


def test_exts(shooter):
    shooter._check_exts(['ass'])
    with pytest.raises(ExtError):
        shooter._check_exts(['Ext'])


def test_search(shooter):
    if not os.path.exists(VIDEOFILE):
        pytest.skip('test video file not exists')
    else:
        subinfos = shooter.search_subs(VIDEOFILE)
        assert len(subinfos) > 0