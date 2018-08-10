:: run test
set DIR="%cd%"

echo
echo "Start testing..."
pipenv run test

:: packaging
echo
echo "Start building..."
del /S /Q dist/*
pipenv run build

:: pyinstaller packaing executable app
echo
echo "Start building app..."
cd app
./build.bat

cd %DIR%

:: publish to test.pypi
echo
echo "Start upload subfinder to test.pypi"
pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*



