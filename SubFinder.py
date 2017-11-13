#!/usr/bin/env python
#-*- coding: utf8 -*-
from __future__ import print_function
import hashlib
import os
import requests
import sys
import mimetypes
import threading
import argparse
import tempfile
import shutil

# python3 不支持內建file对象
if sys.version_info.major == 3:
    from io import IOBase
    file = IOBase


session = requests.Session()
# session.verify = False

def GetRequest(*args, **kwargs):
    return session.get(*args, **kwargs)

def PostRequest(*args, **kwargs):
    return session.post(*args, **kwargs)

POST_URL = 'https://www.shooter.cn/api/subapi.php'

FIND_SUBS = 0                           # 找到的字幕数
SUCCESSED_SUBS = 0                      # 下载成功的字幕数
FAILED_SUBS = 0                         # 下载失败的字幕数
NO_SUBTITLES = []                       # 没有找到字幕的文件列表
VIDEO_EXTS = ['.mkv', '.mp4', '.ts', '.avi', '.wmv']    # 视频文件扩展名

LOCK_FOR_PRINT = threading.Lock()       # 用于保护print信息时不会出现"乱码"
                                        # (i.e 多行信息出现在同一行)
LOCK_FOR_NO_SUBTITLES = threading.Lock()
LOCK_FOR_FIND = threading.Lock()
LOCK_FOR_SUCCESSED = threading.Lock()
LOCK_FOR_FAILED = threading.Lock()

class LanguageError(Exception):
    def __init__(self, msg, *args):
        self.msg = msg
        self.args = args

    def __str__(self):
        return '<LanguageError>: Language must be "Eng" or "Chn".' + \
               'Not %s' % self.msg

class TooManyThreadsError(Exception):
    def __init__(self, threads, max_threads):
        self.threads = threads
        self.max_threads = max_threads
    def __str__(self):
        msg = '<TooManyThreadsError>: Too many thrads,' + \
              'maximum threads is {}, you specify {}'
        return msg.format(self.max_threads, self.threads)

def isVideoFile(file):
    if os.path.isfile(file):
        types = mimetypes.guess_type(file)
        mtype = types[0]
        if (mtype and mtype.split('/')[0] == 'video') or (os.path.splitext(file)[1] in VIDEO_EXTS):
            return True
    return False

def getFileSize(filestring_or_fileobj):
    '''return file size in bytes
    '''
    file_size = 0
    # major = sys.version_info.major
    # minor = sys.version_info.minor
    # if major == 2:
    #     if isinstance(filestring_or_fileobj, basestring):
    #         file_stat = os.stat(filestring_or_fileobj)
    #         file_size = file_stat.st_size
    #     else:
    #         file_size = os.fstat(filestring_or_fileobj.fileno())
    # elif major == 3:
    #     if isinstance(filestring_or_fileobj, str):
    #         file_stat = os.stat(filestring_or_fileobj)
    #         file_size = file_stat.st_size
    #     else:
    #         file_size = os.fstat(filestring_or_fileobj.fileno())
    if isinstance(filestring_or_fileobj, file) or filestring_or_fileobj.fileno:
        file_size = os.fstat(filestring_or_fileobj.fileno()).st_size
    else:
        file_stat = os.stat(filestring_or_fileobj)
        file_size = file_stat.st_size
    return file_size

def computerVideoHash(videofile):
    seek_positions = [None] * 4
    hash_result = []
    with open(videofile, 'rb') as fp:
        total_size = getFileSize(fp)
        seek_positions[0] = 4096
        seek_positions[1] = total_size // 3 * 2
        seek_positions[2] = total_size // 3
        seek_positions[3] = total_size - 8192
        for pos in seek_positions:
            fp.seek(pos, 0)
            data = fp.read(4096)
            m = hashlib.md5(data)
            hash_result.append(m.hexdigest())
        return ';'.join(hash_result)

def getVideoFileFromDir(dir, recursive=False):
    '''从某一目录中获取所有视频文件，返回basename
    '''
    result = []
    append = result.append
    if recursive:
        for root, dirs, files in os.walk(dir):
            for filename in files:
                f = os.path.abspath(os.path.join(root, filename))
                if isVideoFile(f):
                    append(f)
    else:
        for f in os.listdir(dir):
                if isVideoFile(os.path.join(dir, f)):
                    append(os.path.abspath(os.path.join(dir, f)))
    return result

def getSubInfo(videofile, lang):
        '''\
        @param videofile: The absolute path of video file
        @param lang: The subtitle's language, it's must be 'Chn' or 'Eng'
        '''
        filehash = computerVideoHash(videofile)
        pathinfo = os.path.basename(videofile)
        format = 'json'
        if lang not in ('Chn', 'Eng'):
            raise LanguageError(lang)

        payload = {'filehash': filehash,
                   'pathinfo': pathinfo,
                   'format': format,
                   'lang': lang}
        res = PostRequest(POST_URL, data=payload)
        if res.content == '\xff':
            return []
        return res.json()

def downloadSubFromSubinfoList(sub_info_list, basename, lang, output):
    '''\
    @param sub_info_list: It's a list of sub_info,
        the detail infomation about data structure of sub_info can find on
        <https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5
        NZb6_QYZiGI0/preview>
    @oaram basename: video file's basename(no ext).
    @param lang: language of subtitles
    @param output: The output directory of subtitles
    '''
    global FAILED_SUBS
    global SUCCESSED_SUBS
    counters = {'sub': 0, 'idx': 0, 'srt': 0, 'ass': 0}
    for sub_info in sub_info_list:
        subfiles = sub_info['Files']
        delay = sub_info['Delay']
        desc = sub_info['Desc']
        for subfile in subfiles:
            ext = subfile['Ext']
            link = subfile['Link']
            try:
                res = GetRequest(link)
                if res.status_code == requests.codes.ok:
                    counter = counters.setdefault(ext, 0)
                    counter += 1
                    counters[ext] = counter
                    n = '' if counters[ext] == 1 else counters[ext] - 1
                    subfilename = '{basename}.{lang}{counter}.{ext}'.format(
                        basename=basename,
                        lang=lang.lower(),
                        counter=n,
                        ext=ext)
                    LOCK_FOR_PRINT.acquire()
                    print('%s' % subfilename)
                    LOCK_FOR_PRINT.release()
                    if not os.path.exists(output):
                        os.makedirs(output)
                    with open(os.path.join(output, subfilename), 'wb') as fp:
                        fp.write(res.content)
                else:
                    res.raise_for_status()
                    LOCK_FOR_FAILED.acquire()
                    FAILED_SUBS += 1
                    LOCK_FOR_FAILED.release()
            except requests.exceptions.RequestException as e:
                LOCK_FOR_FAILED.acquire()
                FAILED_SUBS += 1
                LOCK_FOR_FAILED.release()
                print(e)
    LOCK_FOR_SUCCESSED.acquire()
    SUCCESSED_SUBS += sum(counters.values())
    LOCK_FOR_SUCCESSED.release()

class DownloadSubThread(threading.Thread):
    def __init__(self, root, files, output=None, languages=['Chn', 'Eng']):
        '''\
        @param root: The root path
        @param files: 视频文件名列表(绝对路径)
        @param output: The output directory that downloading subtitles
            will saving in. default is None, it's same as file's dirname
        '''
        self.root = root
        self.files = files
        self.output = output
        self.languages = languages
        self.session = requests.Session()
        threading.Thread.__init__(self)

    def run(self):
        global FIND_SUBS
        global NO_SUBTITLES
        for f in self.files:
            flag = 0
            for lang in self.languages:
                sub_info_list = getSubInfo(f, lang)
                if sub_info_list:
                    LOCK_FOR_FIND.acquire()
                    # The total number of subtitles
                    N = sum([len(sub_info['Files']) for sub_info in sub_info_list])
                    FIND_SUBS += N
                    LOCK_FOR_FIND.release()
                    # get file's basename(and not endswith ext),
                    # it will use to combining subtitle's filename
                    basename = os.path.splitext(os.path.basename(f))[0]
                    if not self.output:
                        # if self.output is None, then the output directory of
                        # subtitles is same as file's os.path.dirname(file)
                        output = os.path.dirname(f)
                    else:
                        relpath = os.path.relpath(os.path.dirname(f), self.root)
                        output = os.path.join(self.output, relpath)
                    downloadSubFromSubinfoList(sub_info_list, basename, lang, output)
                else:
                    flag += 1
            if flag == len(self.languages):
                # if flag == len(self.languages), that's means
                # can't find video's subtitle.
                LOCK_FOR_NO_SUBTITLES.acquire()
                NO_SUBTITLES.append(f)
                LOCK_FOR_NO_SUBTITLES.release()



def downloadOneSub(videofile, output=None, languages=['Chn', 'Eng']):
    if isVideoFile(videofile):
        # 下载一个字幕
        print('Find 1 video\n')
        root = os.path.dirname(videofile)
        if output is None:
        	output = root
        t = DownloadSubThread(root, [videofile], output, languages)
        t.start()
        t.join()
    else:
        print('%s is not a video file' % args.path)
        sys.exit(1)

def downloadManySubs(path, output=None, num_threads=None,languages=['Chn', 'Eng'],
                     recursive=False, compress=False):
    if compress:
        # 如果指定要压缩字幕，则创建一个临时目录，将下载的字幕全部保存到临时目录
        # 最后再进行压缩
        temp_output = tempfile.mkdtemp(prefix='tmp_subtitles')
    videofiles = list(getVideoFileFromDir(path, recursive))
    threads = (len(videofiles) // 2)
    if threads == 0:
        threads = 1
    if num_threads:
        # 如果线程数超过总的文件数目,则触发异常
        if num_threads > len(videofiles):
            raise TooManyThreadsError(num_threads, len(videofiles))
        threads = num_threads
    # 打印信息
    print('Find %s videos\n' % len(videofiles))
    task_size, remainder = divmod(len(videofiles), threads)
    tasks = []
    for i in range(threads):
        task = videofiles[i * task_size : (i + 1) * task_size]
        tasks.append(task)
    # 将无法均匀分配的任务全部分配给最后一个线程
    if remainder > 0:
        tasks[-1].extend(videofiles[-remainder:])
    thread_list = []
    for task in tasks:
        if compress:
            t = DownloadSubThread(path, task, temp_output, languages)
        else:
            t = DownloadSubThread(path, task, output, languages)
        thread_list.append(t)
    [t.start() for t in thread_list]
    [t.join() for t in thread_list]
    if compress:
        zipname = 'subtitles'
        if not output:
            output = path
        shutil.make_archive(os.path.join(output, zipname), 'zip', temp_output)
        shutil.rmtree(temp_output)
        print('*' * 80)
        print('subtitles.zip saving in %s' % os.path.join(output, zipname))

def main(path, output=None, num_threads=None, languages=['Chn', 'Eng'],
         recursive=False, compress=False):

    if os.path.exists(path):
        if os.path.isfile(path):
            downloadOneSub(os.path.abspath(path), output, languages)

        elif os.path.isdir(path):
            downloadManySubs(os.path.abspath(path), output, num_threads, languages,
                recursive, compress)
        else:
            print('%s is neither a directory nor a file' % path)
            sys.exit(1)

        print('*' * 80)
        tmp = 'Finish.find {} subtitles,{} sucessed,{} failed,' + \
              '{} files not found subtitle'
        print(tmp.format(FIND_SUBS, SUCCESSED_SUBS, FAILED_SUBS,
                        len(NO_SUBTITLES)))
        if NO_SUBTITLES :
            print("Can't found following video file's subtitles:")
            for f in NO_SUBTITLES:
                print('  %s' % os.path.basename(f))
    else:
        # The path doesn't exists.
        print('%s Not exists.' % path)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="The directory contains vedio files")
    parser.add_argument('-o', '--output', help="The output directory of subtitles")
    parser.add_argument('-c', '--compress', action='store_true', default=False,
                        help="Whether compress subtitles, only effective " + \
                        "when argument <path> is a directory")
    parser.add_argument('-n', '--threads', type=int, help="specify number of threads")
    parser.add_argument('-r', '-R', '--recursive', action='store_true',
                        default=False, help="whether recursive directory")
    parser.add_argument('--lang', choices=['Chn', 'Eng'], dest='languages',
                        nargs=1, default=['Chn', 'Eng'],
                        help="chice the language of subtitles, it only can be"+\
                        "'Chn' or 'Eng', if not given, default choose both two")

    args = parser.parse_args()
    path = args.path
    output = args.output
    compress = args.compress
    threads = args.threads
    recursive = args.recursive
    languages = args.languages
    # print args
    main(path, output, threads, languages, recursive, compress)