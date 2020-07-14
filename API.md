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

  | 参数              | 介绍                                                      | 类型                                 |
  | ----------------- | --------------------------------------------------------- | ------------------------------------ |
  | path              | 文件名或者目录                                            | str                                  |
  | languages         | 字幕语言， 如果为 None，则由 `subsearcher_class` 自己决定 | str or [str]                         |
  | exts              | 字幕格式，如果为 None，则由 `subsearcher_class` 自己决定  | str or [str]                         |
  | subsearcher_class | 字幕搜索器，默认是 `ShooterSubSearcher`                   | BaseSubSearcher or [BaseSubSearcher] |

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

  | 参数      | 介绍                 | 类型         |
  | --------- | -------------------- | ------------ |
  | videofile | 视频文件名的绝对路径 | str          |
  | languages | 字幕语言             | str or [str] |
  | exts      | 字幕格式             | str or [str] |

  返回字幕信息列表，字幕信息的格式: `{'link': LINK, 'language': LANGUAGE, 'subname': SUBNAME,'ext': EXT, 'downloaded': False}`。

  格式：

  | 字段       | 介绍                                                                                                                                                           | 类型         |
  | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
  | link       | 字幕文件下载地址，可选，取决于 `downloaded`，如果 `downloaded` 为 False，则必须提供                                                                            | str          |
  | language   | 字幕语言                                                                                                                                                       | str or [str] |
  | exts       | 字幕格式                                                                                                                                                       | str or [str] |
  | subname    | 字幕文件名，可选，取决于 `downloaded`，如果 `downloaded` 为 False，则必须提供                                                                                  | str or [str] |
  | downloaded | `SubSearcher` 是否已经下载好了字幕。如果为 True，表示 `SubSearcher` 已经下载了字幕，那么 `SubFinder` 将不会下载字幕，否者 `SubFinder` 会根据 `link` 下载字幕。 | bool         |

### 自定义字幕搜索器

为了实现你自己的字幕搜索器，你需要：

- 创建一个继承自 `BaseSubSearcher` 的类，实现 `search_subs` 方法，重写 `SUPPORT_LANGUAGES` 和 `SUPPORT_EXTS` 属性。

- 注册你自己的 `SubSeacher` 类。

这里有一个自定义字幕搜索器的 [示例文件](examples/custom_subsearcher.py)。