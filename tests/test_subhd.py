# -*- coding: utf -*-
import pytest
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
