## 利用shooter.org提供的api下载字幕

##### API URL: https://www.shooter.cn/api/subapi.php

API使用说明请参考原文: [射手字幕网API使用说明](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview)

### 介绍
脚本对射手网提供的查找字幕API进行了简单封装，对视频文件进行字模匹配，然后将匹配到的字幕保存到与视频文件相同的目录。

### 参数说明
- path, 包含视频文件的目录。
- -o, --output, 指定字幕保存目录,默认字幕保存在视频文件所在的目录。
- -c, --compress, 指定是否要压缩字幕,压缩包放在指定的output目录,如果output没有指定,
则放在path目录下.注意: 对下载单个视频的字幕无效。
- -n, --threads, 指定线程数。
- -r, --recrusive, 是否递归查找目录下视频文件。默认不递归, 
也就是说只下载path目录下视频文件的字幕。
- --lang, 选择字幕语言, 可选值有:[Chn, Eng], 默认为[Chn,Eng].

### 示例
- 下载单个视频的字幕
```bash
#SubFinder.py /media/xxx.mp4
```
- 下载目录中所有视频的字幕
```bash
#SubFinder.py /media/directory_contains_video_file
```

- 递归下载
```bash
#SubFinder.py -r /media/directory_contains_video_file 
```

- 递归下载并压缩打包
```bash
#SubFinder.py -r -c /media/directory_contains_video_file
```

### 更新历史
- 2016-5-18 添加windows注册表, 鼠标右键直接下载字幕
>NOTE: 将注册表中目录替换为你自己的SubFinder所在的目录