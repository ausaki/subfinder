# -*- coding: utf8 -*-
from __future__ import unicode_literals
from abc import abstractmethod, ABCMeta
from . import exceptions


registered_subsearchers = {}


def register_subsearcher(name, subsearcher_cls):
    """ register a subsearcher, the `name` is a key used for searching subsearchers.
    if the subsearcher named `name` already exists, then it's will overrite the old subsearcher.
    """
    if not issubclass(subsearcher_cls, BaseSubSearcher):
        raise ValueError('{} is not a subclass of BaseSubSearcher'.format(subsearcher_cls))
    registered_subsearchers[name] = subsearcher_cls


def register(subsearcher_cls=None, name=None):
    def decorator(subsearcher_cls):
        if name is None:
            _name = subsearcher_cls.__name__
        else:
            _name = name
        register_subsearcher(_name, subsearcher_cls)
        return subsearcher_cls
    return decorator(subsearcher_cls) if subsearcher_cls is not None else decorator


def get_subsearcher(name, default=None):
    return registered_subsearchers.get(name, default)


def get_all_subsearchers():
    return registered_subsearchers


class BaseSubSearcher(object):
    """ The abstract class for search subtitles.

    You must implement following methods:
    - search_subs
    """
    __metaclass__ = ABCMeta

    SUPPORT_LANGUAGES = []
    SUPPORT_EXTS = []

    @abstractmethod
    def search_subs(self, videofile, languages=None, exts=None, **kwargs):
        """ search subtitles of videofile.

        `videofile` is the absolute(or relative) path of the video file.

        `languages` is the language of subtitle, e.g chn, eng, the support for language is difference, depende on
        implemention of subclass. `languages` accepts one language or a list of language

        `exts` is the format of subtitle, e.g ass, srt, sub, idx, the support for ext is difference,
        depende on implemention of subclass. `ext` accepts one ext or a list of ext

        return a list of subtitle info
        [
            {
                'link': '',     # download link
                'language': '', # language
                'ext': '',      # ext
                'subname': '',  # the filename of subtitles
                'downloaded': False, # it's tell `SubFinder` whether need to download.
            },
            {
                'link': '',
                'language': '',
                'ext': '',
                'subname': '',
            },
            ...
        ] 
        - `link`, it's optional, but if `downloaded` is False, then `link` is required.
        - `language`, it's optional
        - `subname`, it's optional, but if `downloaded` is False, then `subname` is required.
        - `downloaded`, `downloaded` is required. 
            if `downloaded` is True, then `SubFinder` will not download again, 
            otherwise `SubFinder` will download link.
        """
        pass

    def __str__(self):
        if hasattr(self.__class__, 'shortname'):
            name = self.__class__.shortname
        else:
            name = self.__class__.__name__
        return '<{}>'.format(name)

    def __unicode__(self):
        return self.__str__()

    @classmethod
    def _check_languages(cls, languages):
        for lang in languages:
            if lang not in cls.SUPPORT_LANGUAGES:
                raise exceptions.LanguageError(
                    '{} don\'t support "{}" language'.format(cls.__name__, lang))

    @classmethod
    def _check_exts(cls, exts):
        for ext in exts:
            if ext not in cls.SUPPORT_EXTS:
                raise exceptions.ExtError(
                    '{} don\'t support "{}" ext'.format(cls.__name__, ext))

