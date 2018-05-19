:: pyinstaller build script
@echo off

del /S /Q  build dist  
pyinstaller SubFinder.win.spec -y
