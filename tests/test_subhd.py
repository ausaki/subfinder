# -*- coding: utf -*-
from __future__ import unicode_literals, print_function
import pytest
from subfinder.subsearcher import SubHDSubSearcher
from subfinder.subfinder import SubFinder
from subfinder.subsearcher.exceptions import LanguageError, ExtError


@pytest.fixture(scope='module')
def zimuzu():
    s = SubFinder()
    z = SubHDSubSearcher(s)
    return z


def test_languages(zimuzu):
    zimuzu._check_languages(['zh_chs'])
    with pytest.raises(LanguageError):
        zimuzu._check_languages(['fake_lang'])


def test_exts(zimuzu):
    zimuzu._check_exts(['ass'])
    with pytest.raises(ExtError):
        zimuzu._check_exts(['fage_ext'])