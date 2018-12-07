# -*- coding: utf8 -*-
from __future__ import unicode_literals, print_function
import os
import re
import bs4
from .subsearcher import BaseSubSearcher


class ZimukuSubSearcher(BaseSubSearcher):
    """ zimuku 字幕搜索器(https://www.zimuku.cn/)
    """
    SUPPORT_LANGUAGES = ['zh_chs', 'zh_cht', 'en', 'zh_en']
    SUPPORT_EXTS = ['ass', 'srt']
    LANGUAGES_MAP = {
        '简体中文字幕': 'zh_chs',
        '简体中文': 'zh_chs',
        '繁體中文字幕': 'zh_cht',
        '繁體中文': 'zh_cht',
        'English字幕': 'en',
        'English': 'en',
        'english': 'en',
        '双语字幕': 'zh_en',
        '双语': 'zh_en'
    }
    COMMON_LANGUAGES = ['英文', '简体', '繁体']

    API = 'https://www.zimuku.cn/search'
    SUBTITLE_DOWNLOAD_LINK = 'http://www.subku.net/dld/'

    _cache = {}
    shortname = 'zimuku'

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
            ele_a = item.select('p.tt > a')
            if not ele_a:
                continue
            link = ele_a[0].get('href')
            title = ele_a[0].get_text().strip()
            subgroups.append({
                'title': title,
                'link': link,
            })
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
        subgroup = subgroups[0] if subgroups else None
        return subgroup

    def _get_subinfo_list(self, videoname):
        """ return subinfo_list of videoname
        """
        # searching subtitles
        res = self.session.get(self.API, params={'q': videoname})
        doc = res.content
        referer = res.url
        subgroups = self._parse_search_results_html(doc)
        if not subgroups:
            return []
        subgroup = self._filter_subgroup(subgroups)

        # get subtitles
        headers = {
            'Referer': referer
        }
        res = self.session.get(self._join_url(self.API, subgroup['link']))
        doc = res.content
        referer = res.url
        subinfo_list = self._parse_sublist_html(doc)
        return subinfo_list, referer

    def _visit_detailpage(self, detailpage_link, referer):
        detailpage_link = self._join_url(self.API, detailpage_link)
        m = re.search(r'(\d+)\.html', detailpage_link)
        if not m:
            return None
        l = '{}.html'.format(m.group(1))
        downloadpage_link = self._join_url(self.SUBTITLE_DOWNLOAD_LINK, l)
        return downloadpage_link, detailpage_link

    def _visit_downloadpage(self, downloadpage_link, referer):
        """ get the real download link of subtitles.
        """
        headers = {
            'Referer': referer
        }
        res = self.session.get(downloadpage_link, headers=headers)
        doc = res.content
        referer = res.url
        soup = bs4.BeautifulSoup(doc, 'lxml')
        ele_a_list = soup.select('a.btn.btn-sm')
        if not ele_a_list:
            return None
        ele_a = ele_a_list[1]
        download_link = ele_a.get('href')
        return download_link, referer

    def _search_subs(self, videofile, languages, exts):
        videoname = self._get_videoname(videofile)  # basename, not include ext
        videoinfo = self._parse_videoname(videoname)
        keyword = videoinfo.get('title')
        if videoinfo['season'] != 0:
            keyword += '.S{:02d}'.format(videoinfo['season'])

        self._debug('videoinfo: {}'.format(videoinfo))

         # try find subinfo_list from self._cache
        if keyword not in self._cache:
            subinfo_list, referer = self._get_subinfo_list(keyword)
            self._cache[keyword] = (subinfo_list, referer)
        else:
            subinfo_list, referer = self._cache.get(keyword)

        self._debug('subinfo_list: {}'.format(subinfo_list))

        subinfo = self._filter_subinfo_list(
            subinfo_list, videoinfo, languages, exts)

        self._debug('subinfo: {}'.format(subinfo))

        if not subinfo:
            return []
            
        downloadpage_link, referer = self._visit_detailpage(
            subinfo['link'], referer)

        subtitle_download_link, referer = self._visit_downloadpage(
            downloadpage_link, referer)

        filepath, referer = self._download_subs(
            subtitle_download_link, videofile, referer, subinfo['title'])

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
