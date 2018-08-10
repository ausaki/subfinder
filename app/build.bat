:: pyinstaller build script
@echo off

del /S /Q  build dist  
pipenv run pyinstaller -n SubFinder -F -p "../"  app.py
