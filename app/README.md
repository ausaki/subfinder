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



# 问题

在使用 py2app 打包过程中遇到两个主要问题：

1. gevent 兼容性问题

    SubFinder 最初使用 gevent 进行并发下载字幕。当运行打包好的 SubFinder.app 时，出现“ModuleNotFoundError”的错误，尝试了网上的几个解决方案均无效。

    ```
    错误信息如下，删掉了一部分调用栈信息
    ...
    File "subfinder/subfinder_gevent.pyc", line 2, in <module>
    File "gevent/__init__.pyc", line 87, in <module>
    File "gevent/_hub_local.pyc", line 101, in <module>
    File "gevent/_util.pyc", line 105, in import_c_accel
    File "importlib/__init__.pyc", line 126, in import_module
    ModuleNotFoundError: No module named 'gevent.__hub_local'
    ```

    出错位置是 `gevent/_util.py` 的 105 行，`gevent.__hub_local` 这个模块是一个 C 扩展。

    在 `gevent/_util.py` 中有一个函数负责动态导入模块

    ```
    def import_c_accel(globs, cname):
        """
        Import the C-accelerator for the __name__
        and copy its globals.
        """

        name = globs.get('__name__')

        if not name or name == cname:
            # Do nothing if we're being exec'd as a file (no name)
            # or we're running from the C extension
            return

        from gevent._compat import PURE_PYTHON
        if PURE_PYTHON:
            return

        import importlib
        import warnings
        with warnings.catch_warnings():
            # Python 3.7 likes to produce
            # "ImportWarning: can't resolve
            #   package from __spec__ or __package__, falling back on
            #   __name__ and __path__"
            # when we load cython compiled files. This is probably a bug in
            # Cython, but it doesn't seem to have any consequences, it's
            # just annoying to see and can mess up our unittests.
            warnings.simplefilter('ignore', ImportWarning)
            mod = importlib.import_module(cname)
        # By adopting the entire __dict__, we get a more accurate
        # __file__ and module repr, plus we don't leak any imported
        # things we no longer need.
        globs.clear()
        globs.update(mod.__dict__)

        if 'import_c_accel' in globs:
            del globs['import_c_accel']

    ```

    根据网上找到的一些解决方案，出错原因可能是使用 importlib 动态导入 C 模块的原因。

    附上网上的解决方案：

    ```
    # 在代码最开始出执行 fix_import()
    def fix_import():
        import imp, importlib, sys
        import gevent.__hub_local
        
        original_load_module = imp.load_module
        original_find_module = imp.find_module

        def custom_load_module(name, file, pathname, description):
            if name == 'gevent.__hub_local:
                return sys.modules[name]
            return original_load_module(name, file, pathname, description)

        def custom_find_module(name, path=None):
            if name == 'gevent.__hub_local:
                return (None, None, None)
            return original_find_module(name, path)

        imp.load_module = custom_load_module
        imp.find_module = custom_find_module
    ```

    最终仍然没有解决这个问题，无奈只好用 thread 替换 gevent。

    **参考**

    - [py2app兼容性(Common causes for incompatibility)](http://py2app.readthedocs.io/en/latest/recipes.html)

2. 找不到 CA 证书的问题

    当使用 thread 替换 gevent 后，问题1解决了。可是再次运行打包好的 SubFinder.app 时，出现“找不到 CA 证书”的错误。

    SubFinder 使用到了 `requests`，`requests` 依赖 `certifi` 提供 CA 证书。似乎 py2app 无法很好地处理这种非代码的依赖资源。

    解决方案：

    1. 将 `certifi` 库目录的`cacert.pem` 文件复制到 SubFinder 的 app/assets 目录下
    
    2. 在 setup.py 中添加`cacert.pem`
        
        ```
        ...
        cert_file = 'assets/cacert.pem'
        setup(
            name="SubFinder",
            setup_requires=['py2app'],
            app=['app.py'],
            options={
                "py2app": {
                    "resources": ','.join([cert_file, ])
                }
            }
        )
        ```
    
    3. 在代码最开始处添加下面的代码

        ```
        import os
        os.environ["REQUESTS_CA_BUNDLE"] = "assets/cacert.pem"
        ```
    
    [py2app options](http://py2app.readthedocs.io/en/latest/options.html)

