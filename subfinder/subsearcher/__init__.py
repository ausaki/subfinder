# -*- coding: utf8 -*-

from .subsearcher import (  # noqa: F401
    BaseSubSearcher,
    HTMLSubSearcher,
    register,
    register_subsearcher,
    get_subsearcher,
    get_all_subsearchers,
)
from .shooter import ShooterSubSearcher
from .zimuku import ZimukuSubSearcher
from .subhd import SubHDSubSearcher


def _register_internal_subsearcher():
    register_subsearcher(ShooterSubSearcher.shortname, ShooterSubSearcher)
    register_subsearcher(ZimukuSubSearcher.shortname, ZimukuSubSearcher)
    register_subsearcher(SubHDSubSearcher.shortname, SubHDSubSearcher)


_register_internal_subsearcher()
