#-*- coding: gbk -*-
import hashlib
import os
import requests
import sys
import mimetypes
import threading
import argparse
import tempfile
import shutil

POST_URL = 'https://www.shooter.cn/api/subapi.php'
FIND_SUBS = 0                           # 找到的字幕数
SUCCESSED_SUBS = 0                      # 下载成功的字幕数
FAILED_SUBS = 0                         # 下载失败的字幕数
NO_SUBTITLES = []                       # 没有找到字幕的文件列表
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
        return '<LanguageError>: Language must be "Eng" or "Chn". Not %s' % self.msg

class TooManyThreadsError(Exception):
    def __init__(self, threads, max_threads):
        self.threads = threads
        self.max_threads = max_threads
    def __str__(self):
        msg = '<TooManyThreadsError>: Too many thrads, maximum threads is {},' + \
              'you specify {}'
        return msg.format(self.max_threads, self.threads)

def getFileSize(filestring_or_fileobj):
    '''return file size in bytes
    '''
    if isinstance(filestring_or_fileobj, basestring):
        file_stat = os.stat(filestring_or_fileobj)
        return file_stat.st_size
    stat = os.fstat(filestring_or_fileobj.fileno())
    return stat.st_size

def computerVideoHash(videofile):
    seek_positions = [None] * 4
    hash_result = []
    with open(videofile, 'rb') as fp:
        total_size = getFileSize(fp)
        seek_positions[0] = 4096
        seek_positions[1] = total_size / 3 * 2
        seek_positions[2] = total_size / 3
        seek_positions[3] = total_size - 8192
        for pos in seek_positions:
            fp.seek(pos, 0)
            data = fp.read(4096)
            m = hashlib.md5(data)
            hash_result.append(m.hexdigest())
        return ';'.join(hash_result)

def getVedioFileFromDir(dir):
    '''从某一目录中获取所有视频文件，返回basename
    '''
    for f in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, f)):
            types = mimetypes.guess_type(f)
            mtype = types[0]
            if mtype and mtype.split('/')[0] == 'video':
                yield os.path.abspath(os.path.join(dir, f))

class DownloadSubThread(threading.Thread):
    def __init__(self, files, output, lang, *args, **kwargs):
        '''\
        @param files: 视频文件名列表(绝对路径)
        @param output: 字幕保存目录
        '''
        self.files = files
        self.output = output
        self.lang = lang
        self.session = requests.Session()
        threading.Thread.__init__(self, *args, **kwargs)

    def run(self):
        global FIND_SUBS
        global NO_SUBTITLES
        for f in self.files:
            flag = 0
            for lang in self.lang:
                sub_info_list = self.getSubInfo(f, lang)
                if sub_info_list:
                    LOCK_FOR_FIND.acquire()
                    FIND_SUBS += sum([len(sub_info['Files'])
                                        for sub_info in sub_info_list])
                    LOCK_FOR_FIND.release()
                    # 获得无扩展名的文件名
                    filename = os.path.splitext(os.path.basename(f))[0] 
                    self.downloadSub(sub_info_list, self.output, filename, lang)
                else:
                    flag += 1
            if flag == 2:
                LOCK_FOR_NO_SUBTITLES.acquire()
                NO_SUBTITLES.append(f)
                LOCK_FOR_NO_SUBTITLES.release()
    
    def getSubInfo(self, videofile, lang):
        '''\
        @param videofile: 视频文件的绝对路径
        @param lang: 语言, 可选值有['Chn', 'Eng']
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
        res = self.session.post(POST_URL, data=payload)
        if res.content == '\xff':
            return []
        return res.json()

    def downloadSub(self, sub_info_list, path, filename, lang):
        '''\
        @param sub_info_list: 由api返回的字幕信息列表
        @param path: 字幕保存路径
        @oaram filename: 视频文件名(无扩展名),用于作为字幕的文件名
        '''
        global FAILED_SUBS
        global SUCCESSED_SUBS
        counters = {'sub': 0, 'idx': 0, 'srt': 0}
        for sub_info in sub_info_list:
            subfiles = sub_info['Files']
            delay = sub_info['Delay']
            desc = sub_info['Desc']
            for subfile in subfiles:
                ext = subfile['Ext']
                link = subfile['Link']
                try:
                    res = self.session.get(link)
                    if res.status_code == requests.codes.ok:
                        counter = counters.setdefault(ext, 0)
                        counter += 1
                        counters[ext] = counter
                        n = '' if counters[ext] == 1 else counters[ext]
                        subfilename = '{filename}.{lang}{counter}.{ext}'.format(
                            filename=filename,
                            lang=lang,
                            counter=n,
                            ext=ext)
                        LOCK_FOR_PRINT.acquire()
                        print '%s' % subfilename
                        LOCK_FOR_PRINT.release()
                        with open(os.path.join(path, subfilename), 'wb') as fp:
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
                    print e
        LOCK_FOR_SUCCESSED.acquire()
        SUCCESSED_SUBS += sum(counters.values())
        LOCK_FOR_SUCCESSED.release()
   

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="包含视频的目录名或视频文件名.")
    parser.add_argument('-o', '--output', help="字幕输出目录.")
    parser.add_argument('-c', '--compress', action='store_true', default=False,
                        help="是否压缩字幕,默认不压缩,直接保存在视频所在的目录.")
    parser.add_argument('-n', '--threads', type=int, help="指定线程数")
    parser.add_argument('--lang', choices=['Chn', 'Eng'], type=list, dest='language',
                        help="选择字幕语言, 可选值有:[Chn, Eng], 默认为['Chn', 'Eng']")

    args = parser.parse_args()
    language = args.language
    if language is None:
        language = ['Chn', 'Eng']

    if os.path.exists(args.path):
        if os.path.isfile(args.path):
            # 判断path是文件且是视频文件
            types = mimetypes.guess_type(args.path)
            mtype = types[0]
            if mtype and mtype.split('/')[0] == 'video':
                # 下载一个字幕
                print 'Find 1 video\n'
                output = args.output
                if not output:
                    output = os.path.dirname(args.path)
                t = DownloadSubThread([args.path], output, language)
                t.start()
                t.join()
            else:
                print '%s is not a video file' % args.path
                sys.exit(1)

        elif os.path.isdir(args.path):
            output = args.output
            if not output:
                # 如果没有指定字幕输出目录,则将字幕输出目录指定为视频文件所在目录
                output = args.path
            is_compress = args.compress
            if is_compress:
                # 如果指定要压缩字幕，则创建一个临时目录，将下载的字幕全部保存到临时目录
                # 最后再进行压缩
                temp_output = tempfile.mkdtemp(prefix='tmp_subtitles')
            videofiles = list(getVedioFileFromDir(args.path))
            threads = (len(videofiles) / 5) + 1
            if args.threads:
                # 如果线程数超过总的文件数目,则触发异常
                if args.threads > len(videofiles):    
                    raise TooManyThreadsError(args.threads, len(videofiles))
                threads = args.threads
            # 打印信息
            print 'Find %s videos\n' % len(videofiles)
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
                if is_compress:
                    sub_output = temp_output
                else:
                    sub_output = output
                t = DownloadSubThread(task, sub_output, language)
                thread_list.append(t)
            [t.start() for t in thread_list]
            [t.join() for t in thread_list]
            if is_compress:
                zipname = 'subtitles'
                shutil.make_archive(os.path.join(output, zipname), 'zip', temp_output)
                shutil.rmtree(temp_output)
        else:
            print '%s is neither a directory nor a file' % args.path
            sys.exit(1)

        print '\n'
        print '*' * 80
        tmp = 'Finish.find {} subtitles,{} sucessed,{} failed,' + \
              '{} files not found subtitle'
        print tmp.format(FIND_SUBS, SUCCESSED_SUBS, FAILED_SUBS, len(NO_SUBTITLES))
        if NO_SUBTITLES :
            print  "Can't found following video file's subtitles:"
            for f in NO_SUBTITLES:
                print '  %s' % os.path.basename(f)
    else:
        # 路径不存在
        print '%s Not exists.' % args.path
        sys.exit(1)
