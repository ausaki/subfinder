from __future__ import print_function, unicode_literals
import os
import sys
import argparse


def rm_subtitles(path):
    """ delete all subtitles in path recursively
    """
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
    """ move videos in sub-directory of path to path.
    """
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete-subs',
                        help="delete all subtitles in PATH recursively.")
    parser.add_argument('-m', '--move-videos',
                        help="move all files(like videos, subtitles) in sub-directory of PATH to PATH.")

    args = parser.parse_args()

    if args.delete_subs:
        # try to decode str to unicode in python2
        try:
            args.delete_subs = args.delete_subs.decode(sys.getfilesystemencoding())
        except AttributeError as e:
            pass
        print('Start delete subtitles in {}'.format(args.delete_subs))
        c = rm_subtitles(args.delete_subs)
        print('Done, delete {} subtitles'.format(c))

    if args.move_videos:
        # try to decode str to unicode in python2
        try:
            args.move_videos = args.move_videos.decode(sys.getfilesystemencoding())
        except AttributeError as e:
            print('error')
            pass
        print('Start move videos in {}'.format(args.move_videos))
        c = mv_videos(args.move_videos)
        print('Done, move {} files'.format(c))


if __name__ == '__main__':
    main()
