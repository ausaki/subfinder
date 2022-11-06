# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import bs4

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
from .subsearcher import HTMLSubSearcher, SubInfo


class ZimuzuSubSearcher(HTMLSubSearcher):
    """zimuzu 字幕搜索器(http://www.zimuzu.io/)"""

    SUPPORT_LANGUAGES = ['zh_chs', 'zh_cht', 'en', 'zh_en']
    SUPPORT_EXTS = ['ass', 'srt']

    API_URL = 'https://www.yysub.net/search/index'

    _cache = {}
    shortname = 'zimuzu'

    def __init__(self, subfinder, **kwargs):
        super(ZimuzuSubSearcher, self).__init__(subfinder, **kwargs)

    def _parse_search_result_html(self, doc):
        """
        解析搜索结果页面，返回字幕信息列表
        """
        result = []
        soup = bs4.BeautifulSoup(doc, 'lxml')
        search_item_div_list = soup.select('.search-result > ul > li > .search-item')
        if not search_item_div_list:
            return []
        for item in search_item_div_list:
            subinfo = SubInfo()
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

    def _parse_downloadpage_html(self, doc):
        """解析下载页面，返回下载链接"""
        soup = bs4.BeautifulSoup(doc, 'lxml')
        a = soup.select('.download-box > a.btn-click')
        if a:
            a = a[0]
            link = a.get('href')
            return link
        return ''

    def _get_subinfo_list(self, keyword):
        """根据关键词搜索，返回字幕信息列表"""
        res = self.session.get(self.API_URL, params={'keyword': keyword, 'type': 'subtitle'})
        doc = res.content
        self.referer = res.url
        subinfo_list = self._parse_search_result_html(doc)
        return subinfo_list

    def _visit_detailpage(self, detailpage_link):
        """访问字幕详情页面, 获取字幕下载链接"""
        res = self.session.get(detailpage_link, headers={'Referer': self.referer})
        self.referer = res.url
        parts = urlparse.urlparse(detailpage_link)
        path_parts = parts.path.split('/')
        path_parts.insert(2, 'file')
        path = '/'.join(path_parts)
        url = urlparse.urlunparse((parts.scheme, parts.netloc, path, parts.params, parts.query, parts.fragment))

        # 检查是否需要验证码
        res = self.session.get(url, params={'action': 'check'})
        data = res.json()
        if data['status'] == 1001:
            raise RuntimeError('需要登录')
        elif data['status'] == 5001:
            raise RuntimeError('需要验证码')
        elif data['status'] != 1:
            raise RuntimeError(f'未知错误 {data["status"]}')

        return url

    def _visit_downloadpage(self, downloadpage_link):
        """
        字幕详情页面已经获取了下载链接, 这里什么也不做
        """
        return downloadpage_link
