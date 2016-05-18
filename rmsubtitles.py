import glob
import sys
import os

exts = ['.sub', '.idx', '.srt', '.ass']
path = sys.argv[1]

os.chdir(path)

files = []
[files.extend(glob.glob('*' + ext)) for ext in exts]

for f in files:
    try:
        print 'remove:', f
        os.remove(f)
    except (WindowsError, IOError) as e:
        print 'failed:', e
        continue
    print 'success'