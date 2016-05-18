# -*- coding: utf8 -*-
import os, chardet, sys

EXTS = ('.srt', '.sub', '.idx')
ENCODING = 'utf8'

path = sys.argv[1]

for root, dirs, files in os.walk(path):
    for f in files:
        if os.path.splitext(f)[1] in EXTS:
            with open(os.path.join(root, f), 'rb+') as fp:
                data = fp.read()
                try:
                    new_data = data.decode('utf8').encode('gbk')
                except UnicodeError as e:
                    print 'UnicodeError:', f
                    fp.close()
                    continue
                    
                print 'Success:', f
                fp.seek(0, 0)
                fp.truncate()
                fp.write(new_data)
                fp.close()
