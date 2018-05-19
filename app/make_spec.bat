:: pyinstaller make spec script
@echo off

pyi-makespec -n SubFinder -F -w -p "../"  app.py
move SubFinder.spec SubFinder.win.spec