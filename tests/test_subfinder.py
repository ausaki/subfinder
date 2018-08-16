#! /usr/bin/env python

from __future__ import unicode_literals, print_function
import os
import pytest
from subfinder.subfinder import SubFinder
from subfinder.subsearcher import get_subsearcher
from subfinder.utils import rm_subtitles


def test_search_subs_by_shooter():
    directory = os.path.expanduser('~/Downloads/test/')
    if not os.path.exists(directory):
        pytest.skip('test directory not exists')
    rm_subtitles(directory)
    subfinder = SubFinder(path=directory, subsearcher_class=get_subsearcher('shooter'), debug=True)
    subfinder.start()
    files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
    assert len(files) >= 0 

def test_search_subs_by_zimuku():
    directory = os.path.expanduser('~/Downloads/test/')
    if not os.path.exists(directory):
        pytest.skip('test directory not exists')
    rm_subtitles(directory)
    subfinder = SubFinder(path=directory, subsearcher_class=get_subsearcher('zimuku'), debug=True)
    subfinder.start()
    files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
    assert len(files) >= 0

def test_search_subs_by_zimuzu():
    directory = os.path.expanduser('~/Downloads/test/')
    if not os.path.exists(directory):
        pytest.skip('test directory not exists')
    rm_subtitles(directory)
    subfinder = SubFinder(path=directory, subsearcher_class=get_subsearcher('zimuzu'), debug=True)
    subfinder.start()
    files = [f for f in os.listdir(directory) if f.endswith('.ass') or f.endswith('.srt')]
    assert len(files) >= 0