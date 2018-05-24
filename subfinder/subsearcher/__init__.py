# -*- coding: utf8 -*-

from .subsearcher import (
    BaseSubSearcher, 
    register,
    register_subsearcher, 
    get_subsearcher, 
)
from .shooter import ShooterSubSearcher
from .zimuku import ZimukuSubSearcher

def _register_internal_subsearcher():
    register_subsearcher('default', ShooterSubSearcher)
    register_subsearcher(ShooterSubSearcher.__shortname__, ShooterSubSearcher)
    register_subsearcher('zimuku', ZimukuSubSearcher)

_register_internal_subsearcher()