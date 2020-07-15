# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import re
from re import match
import bs4
from .subsearcher import BaseSubSearcher


class ZimukuSubSearcher(BaseSubSearcher):
    """ zimuku 字幕搜索器(https://www.zimuku.cn/)
    """
    SUPPORT_LANGUAGES = ['zh_chs', 'zh_cht', 'en', 'zh_en']
    SUPPORT_EXTS = ['ass', 'srt']

    API_URL = 'http://www.zimuku.la/search/'

    _cache = {}
    shortname = 'zimuku'

    def _parse_downloadcount(self, text):
        """ parse download count
        text format maybe:
        - pure number: 1000
        - number + unit: 1万
        """
        unit_map = {
            '千': 1000,
            '万': 10000,
            '百万': 1000000,
        }

        m = re.match(r'^(\d+(?:\.\d+)?)(\w{0,2})$', text, re.UNICODE)
        if m:
            n = float(m.group(1))
            u = m.group(2)
            u = unit_map.get(u, 1)
            return int(n * u)
        else:
            return 0

    def _parse_search_results_html(self, doc):
        """ parse search result html, return subgroups
        subgroups: [{ 'title': title, 'link': link}]
        """
        subgroups = []
        soup = bs4.BeautifulSoup(doc, 'lxml')
        ele_divs = soup.select('div.item.prel')
        if not ele_divs:
            return subgroups
        for item in ele_divs:
            info = {'title': '', 'link': '', 'sublist': []}
            ele_a = item.select('p.tt > a')
            if not ele_a:
                continue
            info['link'] = ele_a[0].get('href')
            info['title'] = ele_a[0].get_text().strip()
            sublist = item.select('div.sublist > table td.first > a')
            if sublist:
                info['sublist'] = [sub['title'] for sub in sublist]
            subgroups.append(info)
        return subgroups

    def _parse_sublist_html(self, doc):
        soup = bs4.BeautifulSoup(doc, 'lxml')
        subinfo_list = []
        ele_tr_list = soup.select(
            'div.subs > table tr.odd, div.subs > table tr.even')
        if not ele_tr_list:
            return subinfo_list
        for tr in ele_tr_list:
            subinfo = {
                'title': '',
                'link': '',
                'author': '',
                'exts': [],
                'languages': [],
                'rate': 0,
                'download_count': 0,
            }
            ele_td = tr.find('td', class_='first')
            if ele_td:
                # 字幕标题
                subinfo['title'] = ele_td.a.get('title').strip()
                # 链接
                subinfo['link'] = ele_td.a.get('href').strip()
                # 格式
                ele_span_list = ele_td.select('span.label.label-info')
                for ele_span in ele_span_list:
                    ext = ele_span.get_text().strip()
                    ext = ext.lower()
                    ext = ext.split('/')
                    subinfo['exts'].extend(ext)
                # 作者
                ele_span = ele_td.select('span > a > span.label.label-danger')
                if ele_span:
                    subinfo['author'] = ele_span[0].get_text().strip()
            # 语言
            ele_imgs = tr.select('td.tac.lang > img')
            if ele_imgs:
                for ele_img in ele_imgs:
                    language = ele_img.get('title', ele_img.get('alt'))
                    language = self.LANGUAGES_MAP.get(language)
                    subinfo['languages'].append(language)
            # 评分
            ele_i = tr.select('td.tac i.rating-star')
            if ele_i:
                ele_i = ele_i[0]
                m = re.search(r'(\d+)', ele_i.get('title'))
                if m:
                    subinfo['rate'] = m.group(1)
            # 下载次数
            ele_td = tr.select('td.tac')
            if ele_td:
                ele_td = ele_td[-1]
                subinfo['download_count'] = self._parse_downloadcount(
                    ele_td.get_text().strip())
            subinfo_list.append(subinfo)
        return subinfo_list

    def _filter_subgroup(self, subgroups):
        """ choose a best subgroup from `subgroups`
        """
        if not subgroups:
            return None
        videoinfo = self.videoinfo
        season = videoinfo['season']
        if season == 0:
            return subgroups[0]['link']
        for sg in subgroups:
            title = sg['title']
            sublist = sg['sublist']
            for sub in sublist:
                videoinfo_ = self._parse_videoname(sub)
                season_ = videoinfo_['season']
                if season == season_:
                    return sg['link']
        return subgroups[0]['link']

    def _try_js_redirect(self, doc):
        pattern = r'url\s*=\s*[\'"]([^;\'"]+?)[\'"]\s*\+\s*url;'
        matches = re.findall(pattern, doc)
        path = ''.join(reversed(matches))
        return path

    def _get_subinfo_list(self, keyword):
        """ return subinfo_list of videoname
        """
        # searching subtitles
        res = self.session.get(self.API_URL, params={'q': keyword}, headers={'Referer': self.referer})
        doc = res.text
        self.referer = res.url
        subgroups = self._parse_search_results_html(doc)
        if not subgroups:
            self._debug('no subgroups, maybe js redirect')
            redirect_url = self._try_js_redirect(doc)
            if not redirect_url:
                self._debug('no luck, can\'t find any js redirect url')
                return []
            redirect_url = self._join_url(self.referer, redirect_url)
            res = self.session.get(redirect_url, headers={'Referer': self.referer})
            doc = res.text
            self.referer = res.url
            subgroups = self._parse_search_results_html(doc)
            if not subgroups:
                self._debug('last try, no subgroups')
                return []

        subtitle_url = self._filter_subgroup(subgroups)
        subtitle_url = self._join_url(self.API_URL, subtitle_url)
        # get subtitles
        res = self.session.get(subtitle_url, headers={'Referer': self.referer})
        doc = res.text
        self.referer = res.url
        subinfo_list = self._parse_sublist_html(doc)
        for subinfo in subinfo_list:
            subinfo['link'] = self._join_url(res.url, subinfo['link'])
        return subinfo_list

    def _visit_detailpage(self, detailpage_link):
        res = self.session.get(detailpage_link, headers={'Referer': self.referer})
        doc = res.text
        self.referer = res.url
        soup = bs4.BeautifulSoup(doc, 'lxml')
        ele_a_list = soup.select('a#down1')
        if not ele_a_list:
            return None
        ele_a = ele_a_list[0]
        downloadpage_link = self._join_url(res.url, ele_a.get('href'))
        return downloadpage_link

    def _visit_downloadpage(self, downloadpage_link):
        """ get the real download link of subtitles.
        """
        res = self.session.get(downloadpage_link, headers={'Referer': self.referer})
        doc = res.content
        self.referer = res.url
        soup = bs4.BeautifulSoup(doc, 'lxml')
        ele_a_list = soup.select('a.btn.btn-sm')
        if not ele_a_list:
            return None
        ele_a = ele_a_list[1]
        download_link = ele_a.get('href')
        download_link = self._join_url(res.url, download_link)
        return download_link

    def _search_subs(self):
        subinfo = None
        for keyword in self.keywords:
            subinfo_list = self._get_subinfo_list(keyword)
            self._debug('subinfo_list: {}'.format(subinfo_list))
            subinfo = self._filter_subinfo_list(subinfo_list)
            self._debug('subinfo: {}'.format(subinfo))
            if subinfo:
                break
        if not subinfo:
            return []

        downloadpage_link = self._visit_detailpage(subinfo['link'])
        self._debug('downloadpage_link: {}'.format(downloadpage_link))
        subtitle_download_link = self._visit_downloadpage(downloadpage_link)
        self._debug('subtitle_download_link: {}'.format(subtitle_download_link))
        filepath = self._download_subs(subtitle_download_link, subinfo['title'])
        self._debug('filepath: {}'.format(filepath))
        subs = self._extract(filepath)
        self._debug('subs: {}'.format(subs))

        return [{
            'link': self.referer,
            'language': subinfo['languages'],
            'ext': subinfo['exts'],
            'subname': subs,
            'downloaded': True
        }] if subs else []
