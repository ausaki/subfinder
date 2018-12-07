# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import os
import re
import bs4
from subfinder.tools.compressed_file import CompressedFile
from .subsearcher import BaseSubSearcher


class ZimuzuSubSearcher(BaseSubSearcher):
    """ zimuzu 字幕搜索器(http://www.zimuzu.io/)
    """
    SUPPORT_LANGUAGES = ['zh_chs', 'zh_cht', 'en', 'zh_en']
    SUPPORT_EXTS = ['ass', 'srt']
    LANGUAGES_MAP = {
        '简体': 'zh_chs',
        '繁體': 'zh_cht',
        '英文': 'en',
        '中英': 'zh_en',
    }
    COMMON_LANGUAGES = ['英文', '简体', '繁体']

    API = 'http://www.zimuzu.io/search/index'
    SUBTITLE_DOWNLOAD_LINK = 'http://www.subku.net/dld/'

    _cache = {}
    shortname = 'zimuzu'

    @classmethod
    def _gen_subname(cls, videofile, language, ext, **kwargs):
        language = []
        orig_subname = kwargs.get('orig_name')
        try:
            for l in cls.COMMON_LANGUAGES:
                if orig_subname.find(l) >= 0:
                    language.append(l)
        except Exception:
            pass
        language = '&'.join(language)
        basename = os.path.basename(videofile)
        basename, _ = os.path.splitext(basename)
        _, ext = os.path.splitext(orig_subname)
        return '{basename}.{language}{ext}'.format(
            basename=basename,
            language=language,
            ext=ext)

    def _parse_search_result_html(self, doc):
        """
        解析搜索结果页面，返回字幕信息列表
        """
        result = []
        soup = bs4.BeautifulSoup(doc, 'lxml')
        search_item_div_list = soup.select(
            '.search-result > ul > li > .search-item')
        if not search_item_div_list:
            return []
        for item in search_item_div_list:
            subinfo = {
                'title': '',
                'link': '',
                'author': 'zimuzu',
                'exts': [],
                'languages': [],
                'rate': 0,
                'download_count': 0,
            }
            a = item.find('a')
            if not a:
                continue
            url = a.get('href')
            subinfo['link'] = self._join_url(self.API, url)
            zh_title = a.get_text()
            for k, v in self.LANGUAGES_MAP.items():
                if k in zh_title:
                    subinfo['languages'].append(v)
            font = item.find('font', class_="f4")
            en_title = font.string
            subinfo['title'] = en_title
            result.append(subinfo)
        return result

    def _parse_detailpage_html(self, doc):
        """ 解析字幕详情页面
        """
        result = {
            'exts': [],
            'downloadpage_link': ''
        }
        soup = bs4.BeautifulSoup(doc, 'lxml')
        li_list = soup.select('ul.subtitle-info > li')
        for li in li_list:
            if li.string and '【格式】' in li.string:
                s = li.string.lower()
                for ext in self.SUPPORT_EXTS:
                    if ext in s:
                        result['exts'].append(ext)

        a = soup.select('.subtitle-links > a')
        if a:
            a = a[0]
            result['downloadpage_link'] = a.get('href')

        return result

    def _parse_downloadpage_html(self, doc):
        """ 解析下载页面，返回下载链接
        """
        soup = bs4.BeautifulSoup(doc, 'lxml')
        a = soup.select('.download-box > a.btn-click')
        if a:
            a = a[0]
            link = a.get('href')
            return link
        return ''

    def _first_filter_subinfo_list(self, subinfo_list, videoinfo, languages):
        season = videoinfo.get('season')
        episode = videoinfo.get('episode')

        result = []

        for subinfo in subinfo_list:
            title = subinfo.get('title')
            languages_ = subinfo.get('languages')
            videoinfo_ = self._parse_videoname(title)
            season_ = videoinfo_.get('season')
            episode_ = videoinfo_.get('episode')
            
            if (season == season_ and
                episode == episode_ and
                    set(languages_).intersection(set(languages))):

                result.append(subinfo)

        return result

    def _get_subinfo_list(self, keyword):
        """根据关键词搜索，返回字幕信息列表
        """
        res = self.session.get(
            self.API, params={'keyword': keyword, 'search_type': 'subtitle'})
        doc = res.content
        referer = res.url
        subinfo_list = self._parse_search_result_html(doc)

        return subinfo_list, referer

    def _visit_detailpage(self, detailpage_link, referer):
        """访问字幕详情页面，解析出下载页面的地址
        """
        headers = {'Referer': referer}
        res = self.session.get(detailpage_link, headers=headers)
        referer = res.url
        doc = res.content
        result = self._parse_detailpage_html(doc)
        return result, referer

    def _visit_downloadpage(self, downloadpage_link, referer):
        headers = {'Referer': referer}
        res = self.session.get(downloadpage_link, headers=headers)
        referer = res.url
        doc = res.content
        download_link = self._parse_downloadpage_html(doc)
        return download_link, referer

    def _get_keyword(self, videoinfo):
        """ 获取关键词
        """
        keyword = videoinfo.get('title')
        if videoinfo['season'] != 0:
            keyword += '.S{:02d}'.format(videoinfo['season'])
        if videoinfo['episode'] != 0:
            keyword += '.E{:02d}'.format(videoinfo['episode'])
        # replace space with '+'
        keyword = re.sub(r'\s+', '+', keyword)
        return keyword

    def _search_subs(self, videofile, languages, exts):
        videoname = self._get_videoname(videofile)
        videoinfo = self._parse_videoname(videoname)
        keyword = self._get_keyword(videoinfo)

        self._debug('videoinfo: {}'.format(videoinfo))

        # try find subinfo_list from self._cache
        if keyword not in self._cache:
            subinfo_list, referer = self._get_subinfo_list(keyword)
            self._cache[keyword] = (subinfo_list, referer)
        else:
            subinfo_list, referer = self._cache.get(keyword)

        self._debug('subinfo_list: {}'.format(subinfo_list))

        # 初步过滤掉无关的字幕
        subinfo_list = self._first_filter_subinfo_list(
            subinfo_list, videoinfo, languages)

        self._debug('subinfo_list: {}'.format(subinfo_list))

        # 补全字幕信息中的 exts 字段
        for subinfo in subinfo_list:
            detail_info, referer = self._visit_detailpage(
                subinfo['link'], referer)
            subinfo['exts'] = detail_info['exts']

        subinfo = self._filter_subinfo_list(
            subinfo_list, videoinfo, languages, exts)
        
        self._debug('subinfo: {}'.format(subinfo))

        if not subinfo:
            return []

        detail_info, referer = self._visit_detailpage(subinfo['link'], referer)
        downloadpage_link = detail_info['downloadpage_link']

        download_link, referer = self._visit_downloadpage(
            downloadpage_link, referer)

        filepath, referer = self._download_subs(
            download_link, videofile, referer, subinfo['title'])

        self._debug('filepath: {}'.format(filepath))

        subs = self._extract(filepath, videofile, exts)

        self._debug('subs: {}'.format(subs))

        return [{
            'link': referer,
            'language': subinfo['languages'],
            'ext': subinfo['exts'],
            'subname': subs,
            'downloaded': True
        }]
