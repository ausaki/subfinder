#!/usr/bin/env bash

# pyinstaller build script

rm -rf build dist
pipenv run pyinstaller SubFinder.macos.spec -y
