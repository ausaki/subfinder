#!/usr/bin/env bash

# pyinstaller build script

rm -rf build dist

pyinstaller SubFinder.macos.spec -y
