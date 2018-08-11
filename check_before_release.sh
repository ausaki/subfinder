#/usr/bin/env bash

# release subfinder
# 1. update README.md, docs, historys etc
# 2. change version
# 3. run test
# 4. packaging
# 5. publish to pypi
# 6. commit and push to github

set -e

DIR="$(pwd)"

# run test
echo
echo "Start testing..."
pipenv run test

# packaging
echo
echo "Start building..."
rm -rf dist/*
pipenv run build

# pyinstaller packaing executable app
echo
echo "Start building app..."
cd app
./build.sh