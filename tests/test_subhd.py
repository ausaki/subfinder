# -*- coding: utf -*-
from __future__ import unicode_literals, print_function
import pytest
import pathlib
from subfinder.subsearcher import SubHDSubSearcher
from subfinder.subfinder import SubFinder
from subfinder.subsearcher.exceptions import LanguageError, ExtError


@pytest.fixture(scope='module')
def subhd():
    s = SubFinder()
    z = SubHDSubSearcher(s)
    return z


def test_languages(subhd):
    subhd._check_languages(['zh_chs'])
    with pytest.raises(LanguageError):
        subhd._check_languages(['fake_lang'])


def test_exts(subhd):
    subhd._check_exts(['ass'])
    with pytest.raises(ExtError):
        subhd._check_exts(['fage_ext'])

def test_parse(videofile: pathlib.Path):
    subhd: SubHDSubSearcher = SubHDSubSearcher(SubFinder())
    subhd._prepare_search_subs(videofile)
    subinfo_list = subhd._get_subinfo_list(subhd.keywords[0])
    assert subinfo_list
    subinfo = subinfo_list[0]
    assert subinfo
    assert subinfo['title'] and subinfo['link'] and subinfo['exts'] and subinfo['languages']