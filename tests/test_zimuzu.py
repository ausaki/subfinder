#! /usr/bin/env python
# -*- coding: utf -*-
from __future__ import unicode_literals, print_function
import pathlib
import pytest
from subfinder.subsearcher import ZimuzuSubSearcher
from subfinder.subfinder import SubFinder
from subfinder.subsearcher.exceptions import LanguageError, ExtError


@pytest.fixture(scope='module')
def zimuzu():
    s = SubFinder()
    z = ZimuzuSubSearcher(s)
    return z


def test_languages(zimuzu):
    zimuzu._check_languages(['zh_chs'])
    with pytest.raises(LanguageError):
        zimuzu._check_languages(['fake_lang'])


def test_exts(zimuzu):
    zimuzu._check_exts(['ass'])
    with pytest.raises(ExtError):
        zimuzu._check_exts(['fake_ext'])


def test_parse(videofile: pathlib.Path):
    subfinder = SubFinder(subsearcher_class=ZimuzuSubSearcher)
    zimuzu: ZimuzuSubSearcher = subfinder.subsearcher[0]
    zimuzu._prepare_search_subs(videofile)
    subinfo_list = zimuzu._get_subinfo_list(zimuzu.keywords[0])
    assert subinfo_list
    subinfo = subinfo_list[0]
    assert subinfo
    assert subinfo['title'] and subinfo['link'] and subinfo['languages']
