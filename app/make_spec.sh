#!/usr/bin/env bash

# pyinstaller make spec script

pipenv run pyi-makespec -n SubFinder -F -p "../"  app.py
mv SubFinder.spec SubFinder.macos.spec
