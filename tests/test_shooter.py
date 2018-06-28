#! /usr/bin/env python

from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subsearcher.shooter import ShooterSubSearcher
from subfinder.subsearcher.exceptions import LanguageError, ExtError, ShooterAPIError


@pytest.fixture(scope='module')
def shooter():
    s = ShooterSubSearcher()
    return s


class TestShooterSubSearcher:

    right_hash = '54b690dcdbd19e9675042612b9c25143;' + \
        '48d6d334d0c51066f39f09f796c4bebd;' + \
        'd422f9797befa81a0c2ae880b6ceaa34;' + \
        'fddfb48e1bdd219fad1ae5ab2c4c01ed'

    def test_compute_videohash(self, shooter):
        f = '~/Downloads/test/Marvels.Agents.of.S.H.I.E.L.D.S05E21.720p.HDTV.x264-AVS.mkv'
        f = os.path.expanduser(f)
        if not os.path.exists(f):
            pytest.skip('test video file not exists')
        else:
            h = shooter._compute_video_hash(f)
            assert h == self.right_hash

    def test_languages(self, shooter):
        shooter._check_languages(['Chn'])
        with pytest.raises(LanguageError):
            shooter._check_languages(['Lang'])

    def test_exts(self, shooter):
        shooter._check_exts(['ass'])
        with pytest.raises(ExtError):
            shooter._check_exts(['Ext'])

    def test_search_ok(self, shooter, monkeypatch):
        monkeypatch.setattr(shooter, '_compute_video_hash',
                            lambda f: self.right_hash)
        fake_file = '/a/b/c'
        subinfos = shooter.search_subs(
            fake_file, languages=['Chn', 'Eng'], exts=['ass', 'srt'])
        assert len(subinfos) > 0

    def test_search_failed(self, shooter, monkeypatch):
        monkeypatch.setattr(shooter, '_compute_video_hash',
                            lambda f: 'wronghash')
        fake_file = '/a/b/c'
        subinfos = shooter.search_subs(
            fake_file, languages=['Chn', 'Eng'], exts=['ass', 'srt'])
        assert len(subinfos) == 0
