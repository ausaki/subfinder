# subfinder 字幕查找器

subfinder 是一个通用字幕查找器，可以查找字幕并下载。


> 名词约定：
> - subfinder 指的是本项目（工具）。
> - SubFinder 指的是类（class），SubFinder 类是 subfinder 的入口。
> - SubSearcher 指的是类（class），有的时候也泛指继承于 `BaseSubSearcher` 的子类。


## 特性

- 通过射手字幕网提供的 API，可以精确匹配字幕。

- 支持从 [字幕库](https://www.zimuku.cn/) 搜索字幕。

- 支持指定语言和格式查找字幕。

- 自动将字幕下载至和视频文件相同的目录，自动将字幕文件重命名为视频文件名，方便播放器自动加载字幕。

- 支持线程和协程并发下载。

- 支持 python2 和 python3。

## 安装


** 有 3 种方法安装 SubFinder**

1. 从源码安装：

    - `git clone https://github.com/ausaki/subfinder`

    - `cd subfinder`

    - `pip install .` 或者 `python setup.py install`

2. 使用 pip 从 github 安装：

    - `pip install git+https://github.com/ausaki/subfinder`

3. 从 pypi 安装：

    - `pip install subfinder`


安装完成之后，会在 Python 的 scripts 目录下添加一个叫做 subfinder 的可执行文件。

> 在 unix-like 系统中，scripts 目录一般是 `/usr/local/bin`，在 Windows 系统中，scripts 目录一般是 `C:\python\scripts\`。在 Windows 系统中需要将 `C:\python\scripts\` 加入到 `PATH` 中（一般安装 Python 时已经添加了）。

** 更新 **

安装方式不同，更新方法也不同。

第 1 种：

在项目目录执行：

- `git pull`

- `pip install . --upgrade`

第 2 种：

- `pip install git+https://github.com/ausaki/subfinder --upgrade`

第 3 种：

- `pip install subfinder --upgrade`


## 使用方法

### 命令行

- 使用默认字幕查找器查找单个视频的字幕：

    `subfinder /path/to/videofile`

- 使用默认字幕查找器查找目录下（递归目录）所有视频的字幕：

    `subfinder /path/to/directory_contains_video`

- 使用 `zimuku` 查找字幕

    `subfinder /path/to/directory_contains_video -m zimuku`

- 同时使用多个字幕查找器查找字幕

    `subfinder /path/to/directory_contains_video -m shooter zimuku`

    当指定多个字幕查找器时，subfinder 会依次尝试每个字幕查找器去查找字幕，只要有一个字幕查找器返回字幕信息，则不再使用后面的字幕查找器查找字幕。

    ** 注意：** 如果指定了多个 `subsearcher_class`，请不要指定 `languages` 参数，否则可能会出现校验错误（LanguageError），因为每个 `SubSearcher` 支持的语言可能不相同。

参数说明

```bash
$ subfinder -h
usage: subfinder [-h] [-l LANGUAGES [LANGUAGES ...]] [-e EXTS [EXTS ...]]
              [-m METHOD [METHOD ...]] [-s] [-p]
              path

A general subsearcher, support for custom SubSearcher

positional arguments:
  path                  the video's filename or the directory contains vedio
                        files

optional arguments:
  -h, --help            show this help message and exit
  -l LANGUAGES [LANGUAGES ...], --languages LANGUAGES [LANGUAGES ...]
                        what's languages of subtitle you want to find
  -e EXTS [EXTS ...], --exts EXTS [EXTS ...]
                        what's formats of subtitle you want to find
  -m METHOD [METHOD ...], --method METHOD [METHOD ...]
                        what's methods you want to use to searching subtitles,
                        defaults to ShooterSubSearcher. support methods:
                        default, shooter, zimuku
  -s, --silence         don't print anything, default to False
  -p, --pause           pause script after subfinder done. this option is used
                        in 'Context Menu on Windows' only

Languages & Exts

languages supported by default: [u'Chn', u'Eng']
exts supported by default: [u'ass', u'srt']

languages supported by shooter: [u'Chn', u'Eng']
exts supported by shooter: [u'ass', u'srt']

languages supported by zimuku: [u'zh_chs', u'zh_cht', u'en', u'zh_en']
exts supported by zimuku: [u'ass', u'srt']

```

### Windows 右键菜单

通过注册表的方式添加右键菜单，使用时选中视频文件或者文件夹，然后点击右键选择查找字幕。

- 下载 [注册表文件](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.reg)，

- 双击注册表文件 subfinder.reg 即可添加注册表到系统中。

### MacOS 右键菜单

在 MacOS 中，通过 Automator 的 Service 实现类似于 Windows 中的右键菜单功能。

- [下载 workflow](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.workflow.tar.gz)。

- 解压 subfinder.workflow.tar.gz。

- 将解压出的 subfinder.workflow 复制到 / Users/YourName/Library/Services。

- 选中视频文件或目录，右键弹出菜单，选择 “服务（Services）” -> “查找字幕”。

如果想要了解如何配置 workerflow，可以参考:
- [MacOS Automator 帮助](https://support.apple.com/zh-cn/guide/automator/welcome/mac)
- [stackexchange 的这篇回答](https://apple.stackexchange.com/questions/238948/osx-how-to-add-a-right-click-option-in-folder-to-open-the-folder-with-an-applic?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa)


## 图形界面

为了方便 Windows 和 MacOS 用户，使用 Python 自带的 Tkinter 写了一个简单的 app。

- Windows 用户下载 SubFinder.exe 文件，直接打开就可以了。界面比较简单，看一下就知道如何使用。

- MacOS 用户下载 SubFinder 文件。界面和 Windows 的一样。

** 注意 **

- gui app 默认同时使用 shooter 和 zimuku 两个字幕搜索器。

- gui app 同样支持命令行参数。


[下载页面](https://github.com/ausaki/subfinder/releases)


## 注意事项

- 由于射手字幕网爬虫的实时性，可能无法查找到最新发布视频的字幕

- 射手字幕网 API 返回的字幕可能出现 “语言不一致” 问题（指定查找英文字幕却返回中文字幕）

- 请使用系统自带的 Python 环境安装 SubFinder，如果使用虚拟环境，会导致 ** 右键菜单 ** 失效（路劲错误，找不到 subfinder）。如果出现此类错误，可以在 `/usr/local/bin` 中建立 subfinder 的软连接。

    `ln -s /path/to/real/subfinder /usr/local/bin/subfinder`


## 扩展

subfinder 的定位是支持第三方扩展的通用字幕查找器。

### subfinder 架构

**class subfinder.subfinder.SubFinder**

`SubFinder` 类定义在 `subfiner/subfiner.py` 中。

`SubFinder` 负责的功能有：

- 收集指定目录下所有的视频文件。

- 调用指定的 `SubSearcher` 查找字幕。

- 下载字幕。

方法：

- `__init__(self, path='./', languages=None, exts=None, subsearcher_class=None, **kwargs)`

    | 参数 | 介绍 | 类型 |
    |-|-|-|
    |path | 文件名或者目录 | str|
    |languages | 字幕语言， 如果为 None，则由 `subsearcher_class` 自己决定 | str or [str]|
    |exts | 字幕格式，如果为 None，则由 `subsearcher_class` 自己决定 | str or [str]|
    |subsearcher_class | 字幕搜索器，默认是 `ShooterSubSearcher`| BaseSubSearcher or [BaseSubSearcher]|

    ** 注意：** 如果指定了多个 `subsearcher_class`，请不要指定 `languages` 参数，否则可能会出现校验错误（LanguageError），因为每个 `SubSearcher` 支持的语言可能不相同。

- `start()`

    开始查找字幕

- `done()`

    查找字幕完成后调用，进行一些收尾工作。

你基本上不用修改 `SubFinder` 类，只需要自定义 `SubSearcher` 即可。

更多关于 `SubFinder` 的细节请查看源码。

`SubFinder` 默认是单线程的，效率有点低，因此基于 `SubFinder` 实现了两个分别基于 gevent 和 thread 的子类。

**class subfinder.subfinder_thread.SubFinderThread**

`SubFinderThread` 类定义在 `subfiner/subfiner_thread.py` 中，`SubFinderThread` 重写了 `SubFinder` 的 `_init_pool` 方法，使用线程池去查找字幕和下载字幕。

**class subfinder.subfinder_gevent.SubFinderGevent**

`SubFinderGevent` 类定义在 `subfiner/subfiner_gevent.py` 中，`SubFinderGevent` 重写了 `SubFinder` 的 `_init_pool` 方法，使用协程池去查找字幕和下载字幕。

如果使用 `SubFinderGevent` ，需要在你的入口文件的第一行进行 patch:

    `from gevent import monkey;monkey.patch_all()`


**class subfinder.subsearcher.SubSearcher**

`SubSearcher` 类定义在 `subfinder/subsearcher.py 中 `，`SubSearcher` 负责查找字幕。

类属性：

- `SUPPORT_LANGUAGES`， 支持的字幕语言， 如 chn、eng。`SUPPORT_LANGUAGES` 用于检查命令行的 `languages` 参数是否合法。

- `SUPPORT_EXTS`， 支持的字幕格式，如 ass、srt。`SUPPORT_EXTS` 用于检查命令行的 `exts` 参数是否合法。

方法：

- `search_subs(self, videofile, languages=None, exts=None, **kwargs)`， 查找字幕。

    | 参数 | 介绍 | 类型 |
    |-|-|-|
    |videofile | 视频文件名的绝对路径 | str|
    |languages | 字幕语言 | str or [str]|
    |exts | 字幕格式 | str or [str] |

    返回字幕信息列表，字幕信息的格式: `{'link': LINK, 'language': LANGUAGE, 'subname': SUBNAME,'ext': EXT, 'downloaded': False}`。

    格式：

    | 字段 | 介绍 | 类型 |
    |-|-|-|
    |link | 字幕文件下载地址，可选，取决于 `downloaded`，如果 `downloaded` 为 False，则必须提供 | str|
    |language | 字幕语言 | str or [str]|
    |exts | 字幕格式 | str or [str] |
    |subname | 字幕文件名，可选，取决于 `downloaded`，如果 `downloaded` 为 False，则必须提供 | str or [str]|
    |downloaded|`SubSearcher` 是否已经下载好了字幕。如果为 True，表示 `SubSearcher` 已经下载了字幕，那么 `SubFinder` 将不会下载字幕，否者 `SubFinder` 会根据 `link` 下载字幕。|bool|


### 自定义字幕搜索器

为了实现你自己的字幕搜索器，你需要：

- 创建一个继承自 `BaseSubSearcher` 的类，实现 `search_subs` 方法，重写 `SUPPORT_LANGUAGES` 和 `SUPPORT_EXTS` 属性。

- 注册你自己的 `SubSeacher` 类。

这里有一个自定义字幕搜索器的 [示例文件](examples/custom_subsearcher.py)。


## 贡献

在使用过程中遇到任何问题，请提交 issue。

如果你希望分享你自己的字幕搜索器，欢迎提交 PR。


## 参考

- [射手字幕网 API 使用文档](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview)

- [射手字幕网 API](https://www.shooter.cn/api/subapi.php)


## License

[MIT License](LICENSE)

## 更新历史

### v1.0.2

- GUI app 同时使用 shooter 和 zimuku 两个字幕搜索器搜索字幕。

- GUI app 支持命令行运行。

- 完善打包 GUI app 的流程。

### v1.0.1

- 完善 ZimukuSubsearcher。

    - 解压字幕压缩包文件时，只解压字幕文件。字幕组上传的字幕压缩包文件中可能包含其它非字幕文件。

    - 完善搜索功能。

- 完善打包方式。

- 修复一些 bug。