#!/usr/bin/env bash

# pyinstaller build script
env="$1"
rm -rf build dist

if [ $env == "production" ]; then
    pyinstaller -n SubFinder -F -w --clean -p "../"  app.py
else
    pyinstaller -n SubFinder -w --clean -p "../"  app.py
fi
