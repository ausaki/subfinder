# Tkinter GUI app

这是一个使用 Tkinter 对 SubFinder 进行了一层封装的 app，可以通过 py2app 或者 py2exe 打包成独立的 app。

# 用法

`python app.py`

# 打包 app

## MacOS

- `pip install py2app`

- `python setup.py py2app`

打包好的 SubFinder.app 在 dist 目录下，在 Finder 中双击SubFinder.app 即可运行。

## Windows

- `pip install py2exe`

- `python setup.py py2exe`

打包好的 SubFinder.exe 在 dist 目录下，双击 SubFinder.exe 即可运行。