import codecs
import os
import sys
import glob
import argparse
from pathlib import Path
from .subsearcher import BaseSubSearcher


def rm_subtitles(path):
    """delete all subtitles in path recursively"""
    sub_exts = ['ass', 'srt', 'sub']
    count = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            _, ext = os.path.splitext(f)
            ext = ext[1:]
            if ext in sub_exts:
                p = os.path.join(root, f)
                count += 1
                print('Delete {}'.format(p))
                os.remove(p)
    return count


def mv_videos(path):
    """move videos in sub-directory of path to path."""
    count = 0
    for f in os.listdir(path):
        f = os.path.join(path, f)
        if os.path.isdir(f):
            for sf in os.listdir(f):
                sf = os.path.join(f, sf)
                if os.path.isfile(sf):
                    new_name = os.path.join(path, os.path.basename(sf))
                    try:
                        os.rename(sf, new_name)
                    except (WindowsError, OSError) as e:
                        print('mv {} happens error: {}'.format(sf, e))
                    else:
                        count += 1
                        print('mv {} to {}'.format(sf, new_name))
    return count


def rename_subtitle(source, template):
    """重命名字幕文件
    @param source: 要重命名的字幕文件
    @param template: 模板，例如：'Friends.S{season:02d}.E{episode:02d}.1080p.5.1Ch.BluRay.ReEnc-DeeJayAhmed.{}.{ext}'
    支持的变量有：season, episode, language, ext
    """
    root = os.path.dirname(source)
    old_name = os.path.basename(source)
    old_name, ext = os.path.splitext(old_name)
    ext = ext[1:]
    info = BaseSubSearcher._parse_videoname(old_name)
    s = info['season']
    e = info['episode']

    _, language = os.path.splitext(old_name)
    language = language[1:]
    if language == '':
        language = 'UNKNOWN'

    new_name = template.format(season=s, episode=e, language=language, ext=ext)
    new_file = os.path.join(root, new_name)
    os.rename(source, new_file)
    return new_file


def remove_bom(fp):
    bytes = fp.read(1).encode('utf-8')
    if any(bytes.startswith(bom) for bom in [codecs.BOM32_LE, codecs.BOM32_BE, codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE, codecs.BOM_UTF8]):
        return
    fp.seek(0)


def parse_hhmmssms_to_ms(hhmmssms, sep=':', ms_sep='.'):
    parts = hhmmssms.split(sep, 2)
    h, m = parts[:2]
    s, ms = parts[2].split(ms_sep)
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)


def format_ms_to_hhmmssms(ms, sep=':', ms_sep='.'):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    h, m, s, ms = ['{:02d}'.format(x) for x in [h, m, s, ms]]
    return sep.join([h, m, ms_sep.join([s, ms])])


def sync_ass(subtitle_file: Path, delay: float):
    target = subtitle_file.with_suffix(subtitle_file.suffix + '.tmp')
    target_fp = open(target, 'w', encoding='utf-8')
    with open(subtitle_file, 'r', encoding='utf-8') as fp:
        remove_bom(fp)
        block_events = False
        format_fields = -1
        format_start_idx = -1
        format_end_idx = -1

        for line in fp:
            striped_line = line.strip()
            # empty line
            if not striped_line:
                target_fp.write(line)
                continue
            # comment
            if striped_line.startswith(';'):
                target_fp.write(line)
                continue
            # config block
            if striped_line[0] == '[' and striped_line[-1] == ']':
                block_name = striped_line[1:-1]
                block_events = block_name.lower() == 'events'
                target_fp.write(line)
                continue

            # k/v config line
            try:
                key, value = striped_line.split(':', 1)
            except ValueError:
                print(striped_line)
            k = key.lower()
            v = value.strip()

            # format line
            if block_events and k == 'format':
                parts = [p.strip().lower() for p in v.split(',')]
                format_fields = len(parts)
                format_start_idx = parts.index('start')
                format_end_idx = parts.index('end')
                target_fp.write(line)
                continue

            # not dialogue
            if k != 'dialogue' or format_fields <= 0:
                target_fp.write(line)
                continue

            # dialogue line
            parts = [p.strip() for p in v.split(',', format_fields - 1)]
            start = parse_hhmmssms_to_ms(parts[format_start_idx])
            end = parse_hhmmssms_to_ms(parts[format_end_idx])
            start += delay
            end += delay
            parts[format_start_idx] = format_ms_to_hhmmssms(start)
            parts[format_end_idx] = format_ms_to_hhmmssms(end)
            new_value = ','.join(parts)
            line = '{}: {}\n'.format(key, new_value)
            target_fp.write(line)
    target_fp.close()
    subtitle_file.rename(subtitle_file.with_suffix(subtitle_file.suffix + '.bak'))
    target.rename(subtitle_file)


def sync_srt(subtitle_file: Path, delay: float):
    target = subtitle_file.with_suffix(subtitle_file.suffix + '.tmp')
    target_fp = open(target, 'w', encoding='utf-8')
    with open(subtitle_file, 'r', encoding='utf-8') as fp:
        remove_bom(fp)
        sub_index = -1
        find_sub_index = False
        for line in fp:
            striped_line = line.strip()
            # empty line
            if not striped_line:
                target_fp.write(line)
                continue
            # subtitle index
            if striped_line.isdigit():
                i = int(striped_line)
                if i == sub_index + 1:
                    find_sub_index = True
                    sub_index = i
                target_fp.write(line)
                continue
            # time line
            if find_sub_index:
                find_sub_index = False
                parts = striped_line.split(' --> ')
                start = parse_hhmmssms_to_ms(parts[0], ms_sep=',')
                end = parse_hhmmssms_to_ms(parts[1], ms_sep=',')
                start += delay
                end += delay
                parts[0] = format_ms_to_hhmmssms(start, ms_sep=',')
                parts[1] = format_ms_to_hhmmssms(end, ms_sep=',')
                line = ' --> '.join(parts) + '\n'
                target_fp.write(line)
                continue
            # subtitle text
            target_fp.write(line)
    target_fp.close()
    subtitle_file.rename(subtitle_file.with_suffix(subtitle_file.suffix + '.bak'))
    target.rename(subtitle_file)


def sync_subtitle_time(subtitle_file, delay):
    subtitle_file = Path(subtitle_file)
    if subtitle_file.suffix == '.ass':
        sync_ass(subtitle_file, delay)
    elif subtitle_file.suffix == '.srt':
        sync_srt(subtitle_file, delay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete-subs', help="delete all subtitles in PATH recursively.")
    parser.add_argument(
        '-m', '--move-videos', help="move all files(like videos, subtitles) in sub-directory of PATH to PATH."
    )
    parser.add_argument('-r', '--rename-sub', nargs=2, help="rename subtitle.")
    parser.add_argument('-s', '--sync-sub', nargs=2, help='sync subtitle time.')

    args = parser.parse_args()

    if args.delete_subs:
        # try to decode str to unicode in python2
        try:
            args.delete_subs = args.delete_subs.decode(sys.getfilesystemencoding())
        except AttributeError:
            pass
        print('Start delete subtitles in {}'.format(args.delete_subs))
        c = rm_subtitles(args.delete_subs)
        print('Done, delete {} subtitles'.format(c))

    if args.move_videos:
        # try to decode str to unicode in python2
        try:
            args.move_videos = args.move_videos.decode(sys.getfilesystemencoding())
        except AttributeError:
            print('error')
            pass
        print('Start move videos in {}'.format(args.move_videos))
        c = mv_videos(args.move_videos)
        print('Done, move {} files'.format(c))

    if args.rename_sub:
        # try to decode str to unicode in python2
        source, template = args.rename_sub
        try:
            source = source.decode(sys.getfilesystemencoding())
        except AttributeError:
            print('error')
            pass
        source_list = glob.glob(source)
        try:
            template = template.decode(sys.getfilesystemencoding())
        except AttributeError:
            print('error')
            pass
        for source in source_list:
            new_file = rename_subtitle(source, template)
            print('rename {} -> {}'.format(source, new_file))

    if args.sync_sub:
        subtitle_file, delay = args.sync_sub
        subtitle_file = Path(subtitle_file).expanduser()
        delay = int(delay)
        sync_subtitle_time(subtitle_file, delay)
        print('sync {} with delay {}ms'.format(subtitle_file, delay))


if __name__ == '__main__':
    main()
