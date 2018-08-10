# Tkinter GUI app

这是一个使用 Tkinter 对 SubFinder 进行了一层封装的 app，可以通过 pyinstaller 打包成独立的 app。

**注意：0.0.7版本以后不在支持 py2app 打包**


# pyinstaller 用法

## MacOS

1. 创建 SubFinder.macos.spec
    
    `bash make_spec.sh`

    make_spec.sh 会在当前目录创建 SubFinder.macos.spec 文件。

3. 创建 app

    `bash build.sh`

    创建好的 SubFinder 放在 dist 目录下。

**SubFinder.macos.spec 是已经修改好的文件，所以可以跳过第1步。**

## Windows

1. 创建 SubFinder.win.spec
    
    `make_spec.bat`

    make_spec.bat 会在当前目录创建 SubFinder.win.spec 文件。

2. 创建 app

    `build.bat`

    创建好的 SubFinder.exe 放在 dist 目录下。

**SubFinder.win.spec 是已经修改好的文件，所以可以跳过第1步。**