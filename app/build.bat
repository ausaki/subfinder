:: pyinstaller build script
@echo off

del /S /Q  build dist  
pipenv run pyinstaller SubFinder.win.spec -y
