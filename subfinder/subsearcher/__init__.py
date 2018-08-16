# -*- coding: utf8 -*-

from .subsearcher import (
    BaseSubSearcher, 
    register,
    register_subsearcher, 
    get_subsearcher, 
    get_all_subsearchers,
)
from .shooter import ShooterSubSearcher
from .zimuku import ZimukuSubSearcher
from .zimuzu import ZimuzuSubSearcher

def _register_internal_subsearcher():
    register_subsearcher('default', ShooterSubSearcher)
    register_subsearcher(ShooterSubSearcher.shortname, ShooterSubSearcher)
    register_subsearcher(ZimukuSubSearcher.shortname, ZimukuSubSearcher)
    register_subsearcher(ZimuzuSubSearcher.shortname, ZimuzuSubSearcher)

_register_internal_subsearcher()