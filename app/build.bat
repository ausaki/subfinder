:: pyinstaller build script
@echo off

del /S /Q  build dist  
poetry run pyinstaller -n SubFinder -F -p "../"  app.py
