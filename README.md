# SubFinder 字幕查找器

SubFinder 是一个字幕查找器，可以自动查找字幕并下载。

目前 SubFinder 只支持通过射手字幕网提供的 API 进行字幕查找，不过 SubFinder 支持自定义字幕查找器，详情参考[扩展](#扩展)


## 特性

- 通过射手字幕网提供的 API，可以精确匹配字幕

- 支持指定语言和格式查找字幕

- 自动将字幕下载至和视频文件相同的目录

- 自动将字幕文件重命名为视频文件名，方便播放器自动加载字幕


## 安装方法

**注意：此安装方法仅适用于具有 Python 环境的系统**

**依赖**

- python3

- pip(可选)

- requests

- gevent


使用自带工具安装

- `git clone https://github.com/ausaki/subfinder`

- `python setup.py install`


使用 pip 安装

`pip install git+https://github.com/ausaki/subfinder`

或者

`pip install subfinder`


## 使用方法

**注意：此使用方法仅适用于具有 Python 环境的系统**

安装完成之后，会在 Python 的 scripts 目录下添加一个叫做 subfinder 的可执行文件。

在 unix-like 系统中，scripts 目录一般是 `/usr/local/bin`，在 Windows 系统中，scripts 目录一般是 `C:\python\scripts\`。在 Windows 系统中需要将`C:\python\scripts\` 加入到 `PATH` 中（一般安装 Python 时已经添加了）。


### 命令行

查找单个视频的字幕

    `subfinder /path/to/videofile` 

查找目录下所有视频的字幕（递归目录）

    `subfinder /path/to/directory_contains_video`

参数说明

```
$ subfinder -h
usage: subfinder [-h] [-l LANGUAGES [LANGUAGES ...]] [-e EXTS [EXTS ...]]
                 [-m METHOD] [-s]
                 path

positional arguments:
  path                  the video's filename or the directory contains vedio
                        files

optional arguments:
  -h, --help            show this help message and exit
  -l LANGUAGES [LANGUAGES ...], --languages LANGUAGES [LANGUAGES ...]
                        what's languages of subtitle you want to find
  -e EXTS [EXTS ...], --exts EXTS [EXTS ...]
                        what's format of subtitle you want to find
  -m METHOD, --method METHOD
                        what's method you want to use to searching subtitles,
                        defaults to ShooterSubSearcher. only support
                        ShooterSubSearcher for now.
  -s, --silence         don't print anything, default to False

```
### Windows 右键菜单

通过注册表的方式添加右键菜单，使用时选中视频文件或者文件夹，然后点击右键选择查找字幕。

- 下载[注册表文件](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.reg)，

- 双击注册表文件 subfinder.reg 即可添加注册表到系统中。

### MacOS 右键菜单

在 MacOS 中，通过 Automator 的 Service 实现类似于 Windows 中的右键菜单功能。

- [下载workeflow](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.workflow.tar.gz)。

- 解压 subfinder.workflow.tar.gz。

- 将解压出的 subfinder.workflow 复制到/Users/YourName/Library/Services。

- 选中视频文件或目录，右键弹出菜单，选择“服务（Services）” -> “查找字幕”。

如果想要了解如何配置 workerflow，可以参考:
- [MacOs Automator 帮助](https://support.apple.com/zh-cn/guide/automator/welcome/mac)
- [stackexchange 的这篇回答](https://apple.stackexchange.com/questions/238948/osx-how-to-add-a-right-click-option-in-folder-to-open-the-folder-with-an-applic?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa)

## 图形界面

为了方便 Windows 和 MacOS 用户，使用 Python 自带的 Tkinter 写了一个简单的app。

[下载页面](https://github.com/ausaki/subfinder/releases)

[Windows, 直接点击这里下载](https://github.com/ausaki/subfinder/releases/download/v0.0.5/SubFinder.exe.tar.gz)

[MaxOS, 直接点击这里下载](https://github.com/ausaki/subfinder/releases/download/v0.0.5/SubFinder.app.tar.gz)


## 注意事项

- 由于射手字幕网爬虫的实时性，可能无法查找到最新发布视频的字幕

- 射手字幕网 API 返回的字幕可能出现“语言不一致”问题（指定查找英文字幕却返回中文字幕）

- 请使用系统自带的 Python 环境安装 SubFinder，如果使用虚拟环境，会导致**右键菜单**失效（路劲错误，找不到 subfinder）。如果出现此类错误，可以在 `/usr/local/bin` 中建立 subfinder 的软连接。

    `ln -s /path/to/real/subfinder /usr/local/bin/subfinder`


## 扩展

SubFinder 是一个通用的字幕查找器，它包含两个主要的类：

- `SubFinder` 
    - 收集指定目录下所有的视频文件
    - 调用`SubSearcher`查找字幕，
    - 下载字幕

- `SubSearcher` 负责查找字幕
    - 类属性：
        - SUPPORT_LANGUAGES 支持的字幕语言， 如chn、eng
        - SUPPORT_EXTS 支持的字幕格式，如ass、srt
    - 方法：
        - search_subs(self, videofile, languages, exts, *args, **kwargs) 查找字幕
        
            该方法接受videofile，languages，exts 参数，返回字幕信息列表

            字幕信息的格式: {'link': LINK, 'language': LANGUAGE, 'subname': SUBNAME,'ext': EXT}

            注意：SUBNAME指的是字幕文件名（即保存路径），最好是绝对路径

为了实现你自己的字幕搜索器，只需要在 subsearcher.py 中创建一个继承自`BaseSubSearcher`的类，实现`search_subs`方法，重写SUPPORT_LANGUAGES和SUPPORT_EXTS，然后在命令行参数中指定`-m`为该类的名称

### 示例
```
# subsearcher.py

class MySubSearch(BaseSubSearch):

    SUPPORT_LANGUAGES = ['chinese', 'english']
    SUPPORT_EXTS = ['ass', 'srt', 'sub']

    def search_subs(self, videofile, languages, exts, *args, **kwargs):
        # search subs for videofile
        return [
            {'link': LINK, 'language': LANGUAGE, 'ext': EXT},
            {'link': LINK, 'language': LANGUAGE, 'ext': EXT}
            ...
            {'link': LINK, 'language': LANGUAGE, 'ext': EXT}
        ]


# 使用 MySubSearcher 搜索字幕
python -m subfinder.run /path/to/videofile -m MySubSearcher

```

## 参考

- [射手字幕网 API 使用文档](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview) 

- [射手字幕网 API](https://www.shooter.cn/api/subapi.php)

