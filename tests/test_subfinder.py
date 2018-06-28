#! /usr/bin/env python

from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subfinder import SubFinder
from subfinder.subsearcher import get_subsearcher
from subfinder.utils import rm_subtitles


@pytest.fixture(scope='module')
def tmp_videofiles(tmpdir_factory):
    files = [
        tmpdir_factory.mktemp('videos').join('file.mkv'),
        tmpdir_factory.mktemp('videos').join('file.mp4'),
        tmpdir_factory.mktemp('videos').join('file.avi'),
    ]
    [f.write(' ') for f in files]
    return [str(f) for f in files]


@pytest.fixture(scope='module')
def tmp_not_videofiles(tmpdir_factory):
    files = [
        tmpdir_factory.mktemp('videos').join('file.abc'),
        tmpdir_factory.mktemp('videos').join('file'),
    ]
    [f.write(' ') for f in files]
    return [str(f) for f in files]


class TestSubFinder:

    def test_videofile(self, tmp_videofiles, tmp_not_videofiles):
        subfinder = SubFinder()
        for f in tmp_videofiles:
            assert subfinder._is_videofile(f)

        not_videofiles = [
            '/path/not/exists/video_file.mkv',
        ]
        for f in not_videofiles:
            assert not subfinder._is_videofile(f)
        for f in tmp_not_videofiles:
            assert not subfinder._is_videofile(f)
    
    def test_search_subs_by_shooter(self):
        directory = os.path.expanduser('~/Downloads/test/')
        if not os.path.exists(directory):
            pytest.skip('test directory not exists')
        rm_subtitles(directory)
        subfinder = SubFinder(path=directory, subsearcher_class=get_subsearcher('shooter'))
        subfinder.start()
        files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
        assert len(files) > 0 
    
    def test_search_subs_by_zimuku(self):
        directory = os.path.expanduser('~/Downloads/test/')
        if not os.path.exists(directory):
            pytest.skip('test directory not exists')
        rm_subtitles(directory)
        subfinder = SubFinder(path=directory, subsearcher_class=get_subsearcher('zimuku'))
        subfinder.start()
        files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
        assert len(files) > 0
