# subfinder 字幕查找器

subfinder 是一个通用字幕查找器，可以查找字幕并下载。

---

[![PyPi](https://img.shields.io/pypi/v/subfinder.svg)](https://pypi.org/project/subfinder/)
[![PyPi - Python Version](https://img.shields.io/pypi/pyversions/subfinder.svg)](https://pypi.org/project/subfinder/)
[![PyPI - License](https://img.shields.io/pypi/l/subfinder.svg)](https://pypi.org/project/subfinder/)
![GitHub last commit](https://img.shields.io/github/last-commit/ausaki/subfinder.svg)

---

Table of Contents
=================

  - [特性](#特性)
  - [安装](#安装)
  - [更新](#更新)
  - [使用方法](#使用方法)
    - [命令行](#命令行)
    - [配置文件](#配置文件)
    - [Windows 右键菜单](#windows-右键菜单)
    - [macOS 右键菜单](#macos-右键菜单)
  - [图形界面](#图形界面)
  - [注意事项](#注意事项)
    - [shooter 字幕搜索器](#shooter-字幕搜索器)
    - [zimuku 字幕搜索器](#zimuku-字幕搜索器)
  - [贡献](#贡献)
  - [参考](#参考)
  - [License](#license)
  - [更新历史](#更新历史)
    - [v2.0.1](#v201)
    - [v2.0.0](#v200)
    - [v1.1.4](#v114)
    - [v1.1.3](#v113)
    - [v1.1.2](#v112)
    - [v1.1.1](#v111)
    - [v1.1.0](#v110)
    - [v1.0.9](#v109)
    - [v1.0.8](#v108)
    - [v1.0.7](#v107)
    - [v1.0.6](#v106)
    - [v1.0.5](#v105)
    - [v1.0.4](#v104)
    - [v1.0.3](#v103)
    - [v1.0.2](#v102)
    - [v1.0.1](#v101)

---

## 特性

- 支持提供的 API，可以精确匹配字幕。

- 支持 [射手字幕网](https://www.shooter.cn/), [字幕库](https://www.zimuku.cn/), [字幕组](http://www.zimuzu.io/), [SubHD](https://subhd.tv)。

## 安装

如果你是 Linux 和 macOS 用户，由于系统自带 Python，推荐使用下面的方法安装 subfinder：

`pip install subfinder`

安装完成之后，会在 Python 的 scripts 目录下添加一个叫做 subfinder 的可执行文件。

> 在 unix-like 系统中，scripts 目录一般是 `/usr/local/bin`，在 Windows 系统中，scripts 目录一般是 `C:\python\scripts\`。在 Windows 系统中需要将 `C:\python\scripts\` 加入到 `PATH` 中（一般安装 Python 时已经添加了）。

接下来你就可以在命令行中使用 subfinder 命令了。

为了方便没有安装 Python 的用户，这里也有已经打包好的可执行文件。[戳这里下载](https://github.com/ausaki/subfinder/releases)。

## 更新

如果 subfinder 是使用 pip 安装的，那么使用 pip 更新，

`pip install subfinder --upgrade`

如果 subfinder 是下载的打包好的可执行文件，那么请重新下载最新的可执行文件并覆盖旧的文件。

## 使用方法

### 命令行

- 使用默认字幕查找器（shooter）查找单个视频的字幕：

  `subfinder /path/to/videofile`

- 使用默认字幕查找器（shooter）查找目录下（递归所有子目录）所有视频的字幕：

  `subfinder /path/to/directory_contains_video`

- 使用指定的字幕查找器查找字幕，例如 zimuku：

  `subfinder /path/to/videofile -m zimuku`

- 同时使用多个字幕查找器查找字幕

  `subfinder /path/to/videofile -m shooter zimuku`

  当指定多个字幕查找器时，subfinder 会依次尝试每个字幕查找器去查找字幕，只要有一个字幕查找器返回字幕信息，则不再使用后面的字幕查找器查找字幕。

  ** 注意：** 如果指定了多个字幕查找器，请不要指定 `languages` 参数，否则可能会出现 `LanguageError` 错误（因为每个 `SubSearcher` 支持的语言可能不相同）。

常用参数说明（详细的参数信息请查看 `subfinder -h`）：

| 参数              | 含义                                                                                               | 必需                                               |
| ----------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| `-l, --languages` | 指定字幕语言，可同时指定多个。每个字幕查找器支持的语言不相同。具体支持的语言请看下文。             | 否，subfinder 默认会下载字幕查找器找到的所有字幕。 |
| `-e, --exts`      | 指定字幕文件格式，可同时指定多个。每个字幕查找器支持的文件格式不相同。具体支持的文件格式请看下文。 | 否，subfinder 默认会下载字幕查找器找到的所有字幕。 |
| `-m,--method`     | 指定字幕查找器，可同时指定多个。                                                                   | 否，subfinder 默认使用 shooter 查找字幕。          |
| `-k, --keyword`   | 手动搜索关键字. 当 SubFinder 使用本身的关键字无法搜索到字幕时, 可以通过这个参数手动指定关键字.     | 否                                                 |
| `--video_exts`    | 视频文件的后缀名（包括.，例如. mp4）                                                               | 否                                                 |
| `--ignore`        | 忽略本地已有的字幕强行查找字幕. 注意: 这可能会覆盖本地已有的字幕. 默认 False。                     | 否                                                 |
| `--exclude`       | 排除文件或目录，支持类似于 shell 的文件匹配模式。详情见下文                                        | 否                                                 |
| `--api_urls`      | 指定字幕搜索器的 API URL。详情见下文                                                               | 否                                                 |
| `-c, --conf`      | 配置文件                                                                                           | 否，SubFinder 默认从~/.subfinder.json 读取。       |
| `-s,--silence`    | 静默运行，不输出日志                                                                               | 否                                                 |
| `--debug`         | 调试模式，输出调试日志                                                                             | 否                                                 |
| `-h,--help`       | 显示帮助信息                                                                                       | 否                                                 |

- `--exclude`, 支持的匹配模式类似于 shell，`*` 匹配任意长度的字符串，`?` 匹配一个字符，`[CHARS]` 匹配 CHARS 中的任一字符。例如：

   - 排除包含 `abc` 的目录：`--exclude '*abc*/'`。注意添加单引号，防止 shell 对其进行扩展。

   - 排除包含 `abc` 的文件：`--exclude '*abc*'`。注意和上个例子的区别，匹配目录时结尾有 `/` 目录分隔符，匹配文件则没有。


- `--api_urls`

  [字幕库](http://www.zimuku.la) 的链接不太稳定，有时候会更换域名，因此提供 `--api_urls` 选项自定义 API URL，以防域名或链接变动。

  `--api_urls` 只接收 JSON 格式的字符串。

  获取正确的 API URL 的方法：

  - 字幕库的 API 一般形如 http://www.zimuku.la/search， 这个 URL 就是网页端 “搜索” 功能的 URL。

  - 字幕组的 API 一般形如 http://www.zmz2019.com/search， 这个 URL 同样是网页端 “搜索” 功能的 URL。

  - SubHD 的 API 一般形如 https://subhd.tv/search. 

  - 射手网的 API 比较稳定，一般不会变动。

  **如果发现字幕网站的 API URL 发生改变, 欢迎提交 issue.**

  配置示例：

  ```
  {
    // 设置字幕库的搜索 API
    "zimuku": "http://www.zimuku.la/search",
    // 设置字幕组的搜索 API
    "zimuzu": "http://www.zmz2019.com/search",
    // 设置字幕组获取字幕下载链接的 API, 注意不包含域名
    "zimuzu_api_subtitle_download": "/api/v1/static/subtitle/detail",
    // 设置 SubHD 的搜索 API
    "subhd": "https://subhd.tv/search",
    // 设置 SubHD 获取字幕下载链接的 API, 注意不包含域名
    "subhd_api_subtitle_download": "/ajax/down_ajax",
    // 设置 SubHD 获取字幕预览的 API, 注意不包含域名
    "subhd_api_subtitle_preview": "/ajax/file_ajax"
  }
  ```

支持的语言和文件格式：

| 字幕查找器 | 语言                                | 文件格式       |
| ---------- | ----------------------------------- | -------------- |
| shooter    | ['zh', 'en']                        | ['ass', 'srt'] |
| zimuku     | ['zh_chs', 'zh_cht', 'en', 'zh_en'] | ['ass', 'srt'] |
| zimuzu     | ['zh_chs', 'zh_cht', 'en', 'zh_en'] | ['ass', 'srt'] |
| subhd      | ['zh_chs', 'zh_cht', 'en', 'zh_en'] | ['ass', 'srt'] |

语言代码：

| 代码   | 含义               |
| ------ | ------------------ |
| zh     | 中文，简体或者繁体 |
| en     | 英文               |
| zh_chs | 简体中文           |
| zh_cht | 繁体中文           |
| zh_en  | 双语               |

### 配置文件

配置文件是 JSON 格式的，支持命令行中的所有选项。命令行中指定的选项优先级高于配置文件的。

配置文件中的 key 一一对应于命令行选项，例如 `-m，--method` 对应的 key 为 `method`。

示例：

```json
{
  "languages": ["zh", "en", "zh_chs"],
  "exts": ["ass", "srt"],
  "method": ["shooter", "zimuzu", "zimuku"],
  "video_exts": [".mp4", ".mkv", ".iso"],
  "exclude": ["excluded_path/", "*abc.mp4"],
  "api_urls": {
    // 设置字幕库的搜索 API
    "zimuku": "http://www.zimuku.la/search",
    // 设置字幕组的搜索 API
    "zimuzu": "http://www.zmz2019.com/search",
    // 设置字幕组获取字幕下载链接的 API, 注意不包含域名
    "zimuzu_api_subtitle_download": "/api/v1/static/subtitle/detail",
    // 设置 SubHD 的搜索 API
    "subhd": "https://subhd.tv/search",
    // 设置 SubHD 获取字幕下载链接的 API, 注意不包含域名
    "subhd_api_subtitle_download": "/ajax/down_ajax",
    // 设置 SubHD 获取字幕预览的 API, 注意不包含域名
    "subhd_api_subtitle_preview": "/ajax/file_ajax"
  }
}
```

### Windows 右键菜单

使用命令行下载字幕还是有一点不方便，特别是需要输入路径。

在 widnows 中，可以通过注册表将 subfinder 添加到右键菜单，使用时右键选中视频文件或者文件夹，然后点击右键菜单中的 “查找字幕”。

![win_menu](assets/subfinder_menu.win.gif)

** 如何添加注册表：**

- 下载 [注册表文件](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.reg)，

- 双击注册表文件 subfinder.reg 即可添加注册表到系统中。

### macOS 右键菜单

在 macOS 中，通过 Automator 的 Service 实现类似于 Windows 中的右键菜单功能。

![subfinder_workflow_service.macos](assets/subfinder_workflow_service.macos.png)

使用方法：

- [下载 workflow](https://raw.githubusercontent.com/ausaki/subfinder/master/assets/subfinder.workflow.tar.gz)。
- 解压 subfinder.workflow.tar.gz。
- 将解压出的 subfinder.workflow 复制到 / Users/YourName/Library/Services。
- 选中视频文件或目录，右键弹出菜单，选择 “服务（Services）” -> “查找字幕”。

** 注意：在 workflow 中，subfinder 的路径是 `/usr/local/bin/subfinder`。**

如果想要了解如何配置 workerflow，可以参考:

- [macOS Automator 帮助](https://support.apple.com/zh-cn/guide/automator/welcome/mac)
- [stackexchange 的这篇回答](https://apple.stackexchange.com/questions/238948/osx-how-to-add-a-right-click-option-in-folder-to-open-the-folder-with-an-applic?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa)

## 图形界面

打包好的可执行文件其实是一个 GUI app，不带任何参数运行的话，会打开一个图形界面。

![subfinder_gui.win](assets/subfinder_gui.win.png)

** 注意 **

- GUI app 默认同时使用 shooter 和 zimuku 两个字幕搜索器。

- GUI app 同样支持命令行参数。

[下载页面](https://github.com/ausaki/subfinder/releases)

## 注意事项

### shooter 字幕搜索器

- 由于射手字幕网爬虫的实时性，可能无法查找到最新发布视频的字幕。
- 射手字幕网 API 返回的字幕可能出现 “语言不一致” 问题（指定查找英文字幕却返回中文字幕）。

### zimuku 字幕搜索器

- zimuku 网站明明有字幕可供下载，subfinder 却提示找不到字幕。可能的原因有：

  - zimuku 字幕搜索器从视频文件名中提取的关键词不够准确，导致搜索结果为空。

  - zimuku 网站修改了 HTML 代码，导致 HTML 解析失败。

- 从 zimuku 网站上下载的字幕一般都是压缩包（zip, rar）。Python 自带的 zipfile 标准库可以解压 zip 压缩包，不过解压 rar 压缩包需要操作系统安装有 unrar 工具。由于 windows 系统安装和配置 unrar 比较麻烦，subfinder 已经內建 unrar.exe 了。对于 Linux 和 macOS 系统的用户，需要自己手动使用系统包管理工具安装 unrar。

## 贡献

在使用过程中遇到任何问题，请提交 issue。

如果你希望分享你自己的字幕搜索器，欢迎提交 PR。

## 参考

- [射手字幕网 API 使用文档](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview)

- [射手字幕网 API](https://www.shooter.cn/api/subapi.php)

## License

[MIT License](LICENSE)

## 更新历史

### v2.0.2

- 更新 gevent 和 bs4 的版本.
### v2.0.1

- 修复打包错误.

### v2.0.0

- 优化部分代码

- 不再支持 Python2.

### v1.1.4

- hotfix

### v1.1.3

- 将参数 `--repeat` 修改为 `--ignore`.

- 添加新参数 `-k, --keyword`.

- 支持 SubHD. SubHD 在下载字幕时经常弹出验证码, 无法通过正常的API获取到字幕的下载链接, 目前的做法是通过 SubHD 的字幕预览功能获取字幕.

- 修复一些 bug.

- 注意: 配置文件中的一些配置项修改了名字, 具体查看文档.
  
### v1.1.2

- 修复 zimuzu 无法正常解析网页的问题 (因为 zimuzu 的网页结构发生了改变).

### v1.1.1

- 修复 subsearcher 的一个 bug.

### v1.1.0

- 使用 poetry 包管理器.

- 修复若干 bug.

### v1.0.9

[issue 27](https://github.com/ausaki/subfinder/issues/27)

- 支持用户配置文件

- 支持用户自定义字幕组和字幕库的 API URL。

- 支持用户自定义视频文件的后缀。

- 支持忽略文件或文件夹。

### v1.0.8

- 修复 zimuku 搜索器的 bug。

### v1.0.7

- 升级 requests 至 2.20.0，修复 requests [安全问题](https://nvd.nist.gov/vuln/detail/CVE-2018-18074)，

### v1.0.6

- 优化了 subsearcher。

- 添加 --debug 选项，方便显示调试信息。

### v1.0.5

- 修复命令行参数 `-l`，`-e` 的问题。

### v1.0.4

- 新增 zimuzu 字幕搜索器。

- 优化代码。

### v1.0.3

- 优化 zimuku 字幕搜索器。

- 內建 unrar.exe，windows 用户不用安装 unrara 了。

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
