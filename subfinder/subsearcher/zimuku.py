# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function
import os
import re
import cgi
try:
    import urlparse
except ImportError as e:
    from urllib import parse as urlparse
import requests
import bs4
from subfinder.tools.compressed_file import CompressedFile
from .subsearcher import BaseSubSearcher


class ZimukuSubSearcher(BaseSubSearcher):
    """ a SubSearcher searching subtitles by zimuku(https://www.zimuku.cn/)
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
    COMMON_LANGUAGES = ['英文', '简体', '繁体', '简体&英文', '繁体&英文', ]

    API = 'https://www.zimuku.cn/search'
    SUBTITLE_DOWNLOAD_LINK = 'http://www.subku.net/dld/'

    _cache = {}
    shortname = 'zimuku'

    def __init__(self, *args, **kwargs):
        super(ZimukuSubSearcher, self).__init__(*args, **kwargs)
        self.session = requests.session()
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'

    def _join_url(self, url, path):
        """ join absolute `url` and `path`(href)
        """
        return urlparse.urljoin(url, path)

    def _parse_videofile(self, videofile):
        """ parse the `videofile` and return it's basename
        """
        name = os.path.basename(videofile)
        name = os.path.splitext(name)[0]
        return name

    def _parse_videoname(self, videoname):
        """ parse videoname and return video info dict
        video info contains:
        - title, the name of video
        - sub_title, the sub_title of video
        - resolution,
        - source,
        -
        - season, defaults to 0
        - episode, defaults to 0
        """
        info = {
            'title': '',
            'season': 0,
            'episode': 0,
            'sub_title': '',
            'resolution': '',
            'source': '',
            'audio_encoding': '',
            'video_encoding': '',
        }
        last_index = 0
        m = re.search(r'[Ss](?P<season>\d+)\.?[Ee](?P<episode>\d+)', videoname)
        if m:
            info['season'] = int(m.group('season'))
            info['episode'] = int(m.group('episode'))
            s, e = m.span()
            info['title'] = videoname[0:s].strip('.')
            last_index = e

        m = re.search(r'(?P<resolution>720[Pp]|1080[Pp]|HR)', videoname)
        if m:
            info['resolution'] = m.group('resolution')
            s, e = m.span()
            if info['title'] == '':
                info['title'] = videoname[0:s].strip('.')

            if info['season'] > 0 and info['episode'] > 0:
                info['sub_title'] = videoname[last_index:s].strip('.')
            last_index = e

        m = re.search(
            r'\.(?P<source>BD|BluRay|BDrip|WEB-DL|HDrip|HDTVrip|HDTV|HD|DVDrip)\.', videoname)
        if m:
            info['source'] = m.group('source')

        m = re.search(
            r'(?P<audio_encoding>mp3|DD5\.1|DDP5\.1|AC3\.5\.1)', videoname)
        if m:
            info['audio_encoding'] = m.group('audio_encoding')

        m = re.search(r'(?P<video_encoding>x264|H264|AVC1|H.265)', videoname)
        if m:
            info['video_encoding'] = m.group('video_encoding')
        return info

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

    def _filter_subinfo_list(self, subinfo_list, videoname, languages, exts):
        """ filter subinfo list base on:
        - season
        - episode
        - languages
        - exts
        -
        return a best matched subinfo
        """
        videoinfo = self._parse_videoname(videoname)
        season = videoinfo.get('season')
        episode = videoinfo.get('episode')
        resolution = videoinfo.get('resolution')
        source = videoinfo.get('source')
        video_encoding = videoinfo.get('video_encoding')
        audio_encoding = videoinfo.get('audio_encoding')

        filtered_subinfo_list_1 = []
        filtered_subinfo_list_2 = []
        filtered_subinfo_list_3 = []
        filtered_subinfo_list_4 = []
        filtered_subinfo_list_5 = []
        filtered_subinfo_list = []

        for subinfo in subinfo_list:
            title = subinfo.get('title')
            videoinfo_ = self._parse_videoname(title)
            season_ = videoinfo_.get('season')
            episode_ = videoinfo_.get('episode')
            resolution_ = videoinfo_.get('resolution')
            source_ = videoinfo_.get('source')
            video_encoding_ = videoinfo_.get('video_encoding')
            audio_encoding_ = videoinfo_.get('audio_encoding')
            languages_ = subinfo.get('languages')

            exts_ = subinfo.get('exts')

            if (season == season_ and
                episode == episode_ and
                set(languages_).intersection(set(languages)) and
                    set(exts_).intersection(set(exts))):

                filtered_subinfo_list_1.append(subinfo)
                if resolution_ == resolution:
                    filtered_subinfo_list_2.append(subinfo)
                    if source_ == source:
                        filtered_subinfo_list_3.append(subinfo)
                        if video_encoding_ == video_encoding:
                            filtered_subinfo_list_4.append(subinfo)
                            if audio_encoding_ == audio_encoding:
                                filtered_subinfo_list_5.append(subinfo)
        if filtered_subinfo_list_5:
            filtered_subinfo_list = filtered_subinfo_list_5
        elif filtered_subinfo_list_4:
            filtered_subinfo_list = filtered_subinfo_list_4
        elif filtered_subinfo_list_3:
            filtered_subinfo_list = filtered_subinfo_list_3
        elif filtered_subinfo_list_2:
            filtered_subinfo_list = filtered_subinfo_list_2
        elif filtered_subinfo_list_1:
            filtered_subinfo_list = filtered_subinfo_list_1

        if not filtered_subinfo_list:
            return None
        # sort by download_count and rate
        sorted_subinfo_list = sorted(filtered_subinfo_list,
                                     key=lambda item: (
                                         item['rate'], item['download_count']),
                                     reverse=True)
        return sorted_subinfo_list[0]

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

    def _get_downloadpage_link(self, subinfo, referer):
        detail_link = subinfo['link']
        detail_link = self._join_url(self.API, detail_link)
        m = re.search(r'(\d+)\.html', detail_link)
        if not m:
            return None
        l = '{}.html'.format(m.group(1))
        downloadpage_link = self._join_url(self.SUBTITLE_DOWNLOAD_LINK, l)
        return downloadpage_link, detail_link

    def _get_subtitle_download_link(self, downloadpage_link, referer):
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

    def _download_subs(self, videofile, subinfo, subtitle_download_link, referer):
        """download archived sub
        """
        root = os.path.dirname(videofile)
        name, _ = os.path.splitext(os.path.basename(videofile))
        _, ext = os.path.splitext(subinfo['title'])
        ext = ext[1:]

        headers = {
            'Referer': referer
        }
        res = self.session.get(subtitle_download_link,
                               headers=headers, stream=True)
        referer = res.url

        # try get ext from Content-Disposition
        content_disposition = res.headers.get('Content-Disposition')
        _, params = cgi.parse_header(content_disposition)
        filename = params.get('filename')
        if filename:
            _, ext = os.path.splitext(filename)
            ext = ext[1:]

        filename = '{}.{}'.format(name, ext)
        filepath = os.path.join(root, filename)
        with open(filepath, 'wb') as fp:
            for chunk in res.iter_content(8192):
                fp.write(chunk)

        return filepath, referer

    def _gen_subname(self, videofile, orig_subname):
        language = []
        try:
            for l in self.COMMON_LANGUAGES:
                if orig_subname.find('.{}.'.format(l)) >= 0:
                    language.append(l)
        except Exception:
            pass
        language = '.'.join(language)
        basename = os.path.basename(videofile)
        basename, _ = os.path.splitext(basename)
        _, ext = os.path.splitext(orig_subname)
        return '{basename}.{language}{ext}'.format(
            basename=basename,
            language=language,
            ext=ext)

    def _extract(self, compressed_file, videofile, subinfo):
        if not CompressedFile.is_compressed_file(compressed_file):
            return [compressed_file]

        root = os.path.dirname(compressed_file)
        subs = []
        cf = CompressedFile(compressed_file)
        for name in cf.namelist():
            if cf.isdir(name):
                continue
            # make `name` to unicode string
            orig_name = CompressedFile.decode_file_name(name)
            _, ext = os.path.splitext(orig_name)
            ext = ext[1:]
            if ext not in subinfo['exts']:
                continue
            subname = self._gen_subname(videofile, orig_name)
            subpath = os.path.join(root, subname)
            cf.extract(name, subpath)
            subs.append(subpath)
        cf.close()
        return subs

    def _search_subs(self, videofile, languages, exts):
        videoname = self._parse_videofile(videofile)  # basename, not ext
        videoinfo = self._parse_videoname(videoname)
        keyword = videoinfo.get('title')
        if videoinfo['season'] != 0:
            keyword += '.S{:02d}'.format(videoinfo['season'])

         # try find subinfo_list from self._cache
        if keyword not in self._cache:
            subinfo_list, referer = self._get_subinfo_list(keyword)
            self._cache[keyword] = (subinfo_list, referer)
        else:
            subinfo_list, referer = self._cache.get(keyword)

        subinfo = self._filter_subinfo_list(
            subinfo_list, videoname, languages, exts)
        if not subinfo:
            return []

        downloadpage_link, referer = self._get_downloadpage_link(
            subinfo, referer)

        subtitle_download_link, referer = self._get_subtitle_download_link(
            downloadpage_link, referer)

        filepath, referer = self._download_subs(
            videofile, subinfo, subtitle_download_link, referer)

        subs = self._extract(filepath, videofile, subinfo)

        return [{
            'link': referer,
            'language': subinfo['languages'],
            'ext': subinfo['exts'],
            'subname': subs,
            'downloaded': True
        }]

    def search_subs(self, videofile, languages=None, exts=None):
        if languages is None:
            languages = [self.SUPPORT_LANGUAGES[0]]
        elif isinstance(languages, str):
            languages = [languages]
        self._check_languages(languages)

        if exts is None:
            exts = self.SUPPORT_EXTS
        elif isinstance(exts, str):
            exts = [exts]
        self._check_exts(exts)

        return self._search_subs(videofile, languages, exts)
