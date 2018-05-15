import os

def rm_subtitles(path):
    """ delete all subtitles in path recursively
    """
    sub_exts = ['ass', 'srt', 'sub']
    for root, dirs, files in os.walk(path):
        for f in files:
            _, ext = os.path.splitext(f)
            ext = ext[1:]
            if ext in sub_exts:
                os.remove(os.path.join(root, f))


