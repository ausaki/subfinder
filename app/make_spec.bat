:: pyinstaller make spec script
@echo off

pipenv run pyi-makespec -n SubFinder -F -p "../"  app.py
move SubFinder.spec SubFinder.win.spec