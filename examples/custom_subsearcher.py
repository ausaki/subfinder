""" this script is introduce how to custom your own SubSearcher

usage:
python subfinder_example.py /path/to/videofile -m MySubSearcher
"""

from subfinder.subsearcher import BaseSubSearcher, register
from subfinder.run import run

# import the thread version of subfinder
from subfinder.subfinder_thread import SubFinderThread as SubFinder


@register
class MySubSearcher(BaseSubSearcher):

    SUPPORT_LANGUAGES = ['chinese', 'english']
    SUPPORT_EXTS = ['ass', 'srt', 'sub']

    def search_subs(self, videofile, languages, exts, *args, **kwargs):
        # search subs for videofile
        return [
            {
                'link': 'http://example.com/subtitle_download',
                'language': 'chn',
                'ext': 'srt',
                'subname': '/local/path/subtitle_name.srt',
            },
            {
                'link': 'http://example.com/subtitle_download',
                'language': 'chn',
                'ext': 'srt',
                'subname': '/local/path/subtitle_name.srt',
            },
            # ...
            {
                'link': 'http://example.com/subtitle_download',
                'language': 'chn',
                'ext': 'srt',
                'subname': '/local/path/subtitle_name.srt',
            },
        ]


if __name__ == '__main__':
    run(SubFinder)
