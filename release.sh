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

version=$1


# run test
pipenv run test

# packaging
rm -rf dist/*
pipenv run build
# pyinstaller packaing executable app
cd app
rm -rf build dist
pipenv run pyinstaller SubFinder.macos.spec -y

# publish to test.pypi
pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# publish to pypi
pipenv run twine upload dist/*

# commit and push to github
git add .
git commit -m "version: $version"
git push



