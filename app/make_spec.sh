#!/usr/bin/env bash

# pyinstaller make spec script

env="$1"

if [ $env == "production" ]; then
    pyi-makespec -n SubFinder -F -w -p "../"  app.py
else
    pyi-makespec -n SubFinder -w -p "../"  app.py
fi
mv SubFinder.spec SubFinder.win.spec
