# -*- mode: python -*-

block_cipher = None
import sys
import shutil

a = Analysis(['app.py'],
             pathex=['../', '/Users/jiaminlu/git_repository/subfinder/app'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SubFinder',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name='SubFinder.app',
             icon=None,
             bundle_identifier=None)

if sys.platform == 'darwin':
    shutil.make_archive('./dist/SubFinder.app', format='gztar', root_dir='./dist', base_dir='./')
elif sys.platform == 'win32':
    shutil.make_archive('./dist/SubFinder.exe', format='gztar', root_dir='./dist', base_dir='./')
