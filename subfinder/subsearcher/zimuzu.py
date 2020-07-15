# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import re
import bs4
try:
    import urlparse
except ImportError as e:
    from urllib import parse as urlparse
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

    API_URL = 'http://www.rrys2020.com/search/index'
    API_SUBTITLE_DOWNLOAD = '/api/v1/static/subtitle/detail'

    _cache = {}
    shortname = 'zimuzu'

    def __init__(self, subfinder, **kwargs):
        super(ZimuzuSubSearcher, self).__init__(subfinder, **kwargs)
        self.API_SUBTITLE_DOWNLOAD = self.api_urls.get(
            'zimuzu_api_subtitle_download', self.__class__.API_SUBTITLE_DOWNLOAD)

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
            subinfo['link'] = self._join_url(self.API_URL, url)
            zh_title = a.get_text()
            for k, v in self.LANGUAGES_MAP.items():
                if k in zh_title:
                    subinfo['languages'].append(v)
            p_eles = item.select('div.fl-info > p')
            if not p_eles:
                continue
            for p_ele in p_eles:
                if '版本' in p_ele.get_text():
                    subinfo['title'] = p_ele.span.string
                    break
            if not subinfo['title']:
                continue
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

    def _first_filter_subinfo_list(self, subinfo_list):
        season = self.videoinfo.get('season')
        episode = self.videoinfo.get('episode')

        result = []

        for subinfo in subinfo_list:
            title = subinfo.get('title')
            languages_ = subinfo.get('languages')
            videoinfo_ = self._parse_videoname(title)
            season_ = videoinfo_.get('season')
            episode_ = videoinfo_.get('episode')

            if (season == season_ and episode == episode_ and set(languages_).intersection(set(self.languages))):
                result.append(subinfo)

        return result

    def _get_subinfo_list(self):
        """根据关键词搜索，返回字幕信息列表
        """
        res = self.session.get(self.API_URL, params={'keyword': self.keyword, 'type': 'subtitle'})
        doc = res.content
        self.referer = res.url
        subinfo_list = self._parse_search_result_html(doc)
        return subinfo_list

    def _visit_detailpage(self, detailpage_link):
        """访问字幕详情页面，解析出下载页面的地址
        """
        res = self.session.get(detailpage_link, headers={'Referer': self.referer})
        self.referer = res.url
        doc = res.content
        result = self._parse_detailpage_html(doc)
        return result

    def _visit_downloadpage(self, downloadpage_link):
        """
        该页面使用Vue动态渲染，通过请求API获取字幕URL
        """
        res = self.session.get(downloadpage_link, headers={'Referer': self.referer})
        self.referer = res.url
        doc = res.text
        # download_link = self._parse_downloadpage_html(doc)
        parts = urlparse.urlparse(downloadpage_link)
        query = urlparse.parse_qs(parts.query)
        code = query.get('code')
        if code is not None:
            code = code[0]
        else:
            return ''
        # parse api url for real downloadable url
        api_url = self.API_SUBTITLE_DOWNLOAD
        pattern = r'(/api/v{\d}+/static/subtitle/detail)\?code='
        match = re.search(pattern, doc)
        if match:
            api_url = match.group(1)
        api_url = self._join_url(self.referer, api_url)
        json_res = self.session.get(api_url, params={'code': code})
        data = json_res.json()
        download_link = data['data']['info']['file']
        return download_link

    def _search_subs(self):
        # try find subinfo_list from self._cache
        if self.keyword not in self._cache:
            subinfo_list = self._get_subinfo_list()
            self._cache[self.keyword] = (subinfo_list, self.referer)
        else:
            subinfo_list, self.referer = self._cache.get(self.keyword)
        self._debug('subinfo_list: {}'.format(subinfo_list))
        # 初步过滤掉无关的字幕
        subinfo_list = self._first_filter_subinfo_list(subinfo_list)
        self._debug('subinfo_list: {}'.format(subinfo_list))

        # 补全字幕信息中的 exts 字段
        for subinfo in subinfo_list:
            detail_info = self._visit_detailpage(subinfo['link'])
            subinfo['exts'] = detail_info['exts']

        subinfo = self._filter_subinfo_list(subinfo_list)
        self._debug('subinfo: {}'.format(subinfo))
        if not subinfo:
            return []

        detail_info = self._visit_detailpage(subinfo['link'])
        downloadpage_link = detail_info['downloadpage_link']
        self._debug('downloadpage_link: {}'.format(downloadpage_link))
        download_link = self._visit_downloadpage(downloadpage_link)
        self._debug('download_link: {}'.format(download_link))
        filepath = self._download_subs(download_link, subinfo['title'])
        self._debug('filepath: {}'.format(filepath))
        subs = self._extract(filepath)
        self._debug('subs: {}'.format(subs))

        return [{
            'link': self.referer,
            'language': subinfo['languages'],
            'ext': subinfo['exts'],
            'subname': subs,
            'downloaded': True
        }]
