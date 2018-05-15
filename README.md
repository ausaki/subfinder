# SubFinder 字幕查找器

SubFinder 是一个字幕查找器，可以自动查找字幕并下载。

目前 SubFinder 只支持通过射手字幕网提供的 API 进行字幕查找，不过 SubFinder 支持自定义字幕查找器，详情参考[扩展](#扩展)


## 特性

- 通过射手字幕网提供的 API，可以精确匹配字幕

- 支持指定语言和格式查找字幕

- 自动将字幕下载至和视频文件相同的目录

- 自动将字幕文件重命名为视频文件名，方便播放器自动加载字幕


## 依赖

- python3

- pip(可选)

- requests

- gevent


## 使用

- `git clone https://github.com/ausaki/subfinder`

- `cd subfinder`

- `pip install .`

- `subfinder /path/to/videofile` or `python main.py /path/to/directory_contains_video`


### 参数说明
```
$ subfinder -h
usage: subfinder [-h] [-o OUTPUT] [-c] [-n THREADS] [-r] [--lang {Chn,Eng}]
                 path

positional arguments:
  path                  The directory contains vedio files

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        The output directory of subtitles
  -c, --compress        Whether compress subtitles, only effective when
                        argument <path> is a directory
  -n THREADS, --threads THREADS
                        specify number of threads
  -r, -R, --recursive   whether recursive directory
  --lang {Chn,Eng}      chice the language of subtitles, it only can be'Chn'
                        or 'Eng', if not given, default choose both two

```


## 注意事项

- 由于射手字幕网爬虫的实时性，可能无法查找到最新发布视频的字幕

- 射手字幕网 API 返回的字幕可能出现“语言不一致”问题（指定查找英文字幕却返回中文字幕）

- ...


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

为了实现你自己的字幕搜索器，只需要在 subfinder.py 中创建一个继承自`BaseSubSearcher`的类，实现`search_subs`方法，重写SUPPORT_LANGUAGES和SUPPORT_EXTS，然后在命令行参数中指定`-m`为该类的名称

### 示例
```
# subfinder.py

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
python main.py /path/to/videofile -m MySubSearcher

```

## 参考

- [射手字幕网 API 使用文档](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview) 

- [射手字幕网 API](https://www.shooter.cn/api/subapi.php)

