from __future__ import print_function
import os
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete-subs',
                        help="delete all subtitles in PATH recursively.the PATH defaults to CWD")

    args = parser.parse_args()
    if args.delete_subs:
        print('Start delete subtitles in {}'.format(args.delete_subs))
        c = rm_subtitles(args.delete_subs)
        print('Done, delete {} subtitles'.format(c))

if __name__ == '__main__':
    main()
