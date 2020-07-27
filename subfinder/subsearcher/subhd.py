import os
import pathlib
import urllib
import bs4
from .subsearcher import HTMLSubSearcher, SubInfo


class SubHDSubSearcher(HTMLSubSearcher):
    """ SubHD 字幕搜索器(https://subhd.tv)
    """
    SUPPORT_LANGUAGES = ['zh_chs', 'zh_cht', 'en', 'zh_en']
    SUPPORT_EXTS = ['ass', 'srt']

    API_URL = 'https://subhd.tv/search/'
    API_SUBTITLE_DOWNLOAD = '/ajax/down_ajax'
    API_SUBTITLE_PREVIEW = '/ajax/file_ajax'

    _cache = {}
    shortname = 'subhd'

    def __init__(self, subfinder, **kwargs):
        super(SubHDSubSearcher, self).__init__(subfinder, **kwargs)
        self.API_SUBTITLE_DOWNLOAD = self.api_urls.get(
            'subhd_api_subtitle_download', self.__class__.API_SUBTITLE_DOWNLOAD)
        self.API_SUBTITLE_PREVIEW = self.api_urls.get(
            'subhd_api_subtitle_preview', self.__class__.API_SUBTITLE_PREVIEW
        )

    def _parse_search_results_html(self, doc):
        """ parse search result html
        """
        soup = bs4.BeautifulSoup(doc, 'lxml')
        subinfo_list = []
        div_list = soup.select('div.mb-4')
        if not div_list:
            return subinfo_list
        for div in div_list:
            subinfo = SubInfo()
            div_title = div.find('div', class_='f12 pt-1')
            if not div_title:
                break
            a = div_title.a
            # 字幕标题
            subinfo['title'] = a.get('title').strip()
            # 链接
            subinfo['link'] = a.get('href').strip()

            div_format = div_title.find_next_siblings('div', limit=1)
            if not div_format:
                break
            div_format = div_format[0]
            # 语言
            format_str = ' '.join(div_format.strings)
            for l1, l2 in self.LANGUAGES_MAP.items():
                if l1 in format_str:
                    subinfo['languages'].append(l2)
            # 格式
            for ext in self.SUPPORT_EXTS:
                if ext in format_str or ext.upper() in format_str:
                    subinfo['exts'].append(ext)
            # 下载次数
            div_download = div_format.find_next_siblings('div', class_='pt-3')
            if not div_download:
                break
            div_download = div_download[0]
            fa_download = div_download.find('i', class_='fa-download')
            dl_str = fa_download.next_sibling
            dl_str = dl_str.replace('次', '')
            subinfo['download_count'] = int(dl_str)
            subinfo_list.append(subinfo)
        return subinfo_list

    def _get_subinfo_list(self, keyword):
        """ return subinfo_list of keyword
        """
        # searching subtitles
        url = self.API_URL
        if not url.endswith('/'): url += '/'
        url += urllib.parse.quote(keyword) 
        res = self.session.get(url)
        doc = res.text
        self.referer = res.url
        subinfo_list = self._parse_search_results_html(doc)
        for subinfo in subinfo_list:
            subinfo['link'] = self._join_url(res.url, subinfo['link'])
        return subinfo_list

    def _visit_detailpage(self, detailpage_link):
        download_link = ''
        res = self.session.get(detailpage_link, headers={ 'Referer': self.referer })
        if not res.ok:
            return download_link
        doc = res.text
        self.referer = res.url
        soup = bs4.BeautifulSoup(doc, 'lxml')
        button_download = soup.find('button', id=True, sid=True)
        if not button_download:
            return download_link
        api_subtitle_url = self._join_url(self.referer, self.API_SUBTITLE_DOWNLOAD)
        params = {
            'sub_id': button_download.get('sid'),
            'dtoken1': button_download.get('dtoken1'),
        }
        res = self.session.post(api_subtitle_url, json=params)
        if not res.ok:
            return download_link
        data = res.json()
        if data['success']:
            download_link = data['url']
        else:
            self.subfinder.logger.info('遇到验证码, 尝试通过字幕预览下载, 如果失败请尝试手动下载: {}'.format(detailpage_link))
        return download_link
    
    def _visit_downloadpage(self, downloadpage_link):
        pass

    def _try_preview_subs(self, detailpage_link):
        subs = []
        root = os.path.dirname(self.videofile)
        api_url = self._join_url(detailpage_link, self.API_SUBTITLE_PREVIEW)
        res = self.session.get(detailpage_link, headers={ 'Referer': self.referer })
        if not res.ok:
            return subs
        doc = res.text
        self.referer = res.url
        soup = bs4.BeautifulSoup(doc, 'lxml')
        a_list = soup.select('a[data-target="#fileModal"][data-sid]')
        if not a_list:
            return subs
        files = []
        for a in  a_list:
            s = a.string.strip()
            if s == '预览':
                sid = a.get('data-sid')
                fname = a.get('data-fname')
                ext = pathlib.PurePath(fname).suffix
                ext = ext[1:]
                if ext in self.exts:
                    files.append((sid, fname))
        
        for sid, fname in files:
            params = {'dasid': sid, 'dafname': fname}
            resp = self.session.post(api_url, data=params)
            if not resp.ok:
                continue
            data = resp.json()
            if not data['success']:
                continue
            filedata = data['filedata']
            origin_file = os.path.basename(fname)
            subname = self._gen_subname(origin_file)
            subname = os.path.join(root, subname)
            with open(subname, 'w') as fp:
                fp.write(filedata)
            subs.append(subname)

        return subs

    def _download_subtitle(self, subinfo):
        subtitle_download_link = self._visit_detailpage( subinfo['link'])
        self._debug('subtitle_download_link: {}'.format(subtitle_download_link))
        subs = None
        if not subtitle_download_link:
            subs = self._try_preview_subs(subinfo['link'])
        else:
            filepath = self._download_subs(subtitle_download_link, subinfo['title'])
            self._debug('filepath: {}'.format(filepath))
            subs = self._extract(filepath)
        self._debug('subs: {}'.format(subs))
        return subs
