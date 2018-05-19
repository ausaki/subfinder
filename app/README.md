# Tkinter GUI app

这是一个使用 Tkinter 对 SubFinder 进行了一层封装的 app，可以通过 pyinstaller 打包成独立的 app。

**注意：0.0.7版本以后不在支持 py2app 打包**


# pyinstaller 用法

## MacOS

1. 创建 SubFinder.macos.spec
    
    `bash make_spec.sh`

    make_spec.sh 会在当前目录创建 SubFinder.macos.spec 文件。

2. 修改 SubFinder.macos.spec（可选）

    1. 支持高分屏
        
        找到下面这段代码
        
        ```
        app = BUNDLE(exe,
                name='SubFinder.app',
                icon=None,
                bundle_identifier=None)
        ```
        
        改为
        
        ```
        app = BUNDLE(exe,
                name='SubFinder.app',
                icon=None,
                bundle_identifier=None,
                info_plist={
                    'NSHighResolutionCapable': 'True'
                })
        ```
    2. 压缩打包

        在 import 处添加
        
        `import shutil`

        在文件末尾添加

        ```
        shutil.make_archive('./dist/SubFinder.app', format='gztar',
                    root_dir='./dist', base_dir='./')
        ```

3. 创建 app

    `bash build.sh`

    创建好的 SubFinder.app 放在 dist 目录下，同时还创建了一份压缩文件 SubFinder.app.tar.gz。

**SubFinder.macos.spec 是已经修改好的文件，所以可以跳过第1步和第2步**

## Windows

1. 创建 SubFinder.win.spec
    
    `make_spec.bat`

    make_spec.bat 会在当前目录创建 SubFinder.win.spec 文件。

2. 创建 app

    `build.bat`

    创建好的 SubFinder.exe 放在 dist 目录下。

**SubFinder.win.spec 是已经修改好的文件，所以可以跳过第1步**