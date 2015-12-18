## 利用shooter.org提供的api下载字幕

##### API: https://www.shooter.cn/api/subapi.php

API使用说明请参考原文: [射手字幕网API使用说明](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview)

### 介绍
该脚本可以找出给定目录下的所有视频文件(默认不递归子目录), 然后利用API下载所有
匹配的中英文字幕。当然, 也可以只下载单个视频对应的字幕.
### 参数说明
- path, path是position argument, 包含视频文件的目录.
- -o, --output, 指定字幕保存目录,默认字幕保存在视频文件所在的目录.
- -c, --compress, 指定是否要压缩字幕,压缩包放在指定的output目录,如果output没有指定,
则放在path目录下.注意: 对下载单个视频的字幕无效.
- -n, --threads, 指定线程数,不能超过目录包含的总视频文件数目.
- -r, --recrusive, 是否递归, 默认不递归, 也就是说只下载path目录下视频文件的字幕.
- --lang, 选择字幕语言, 可选值有:[Chn, Eng], 默认为[Chn,Eng].

### Example
- 下载单个视频的字幕
```bash
F:\WorkFile\github\python-shooter.org-api>SubFinder.py "F:\迅雷下载\fargoS01\Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.mkv"
Find 1 video

Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt


********************************************************************************
Finish.find 6 subtitles,6 sucessed,0 failed,0 files not found subtitle
```
- 下载目录中所有视频的字幕
```bash
F:\WorkFile\github\python-shooter.org-api>SubFinder.py F:\迅雷下载\fargoS01
Find 10 videos

Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
...中间省略
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Chn2.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng2.ass
********************************************************************************
Finish.find 60 subtitles,60 sucessed,0 failed,0 files not found subtitle
```

- 递归下载
```bash
F:\WorkFile\github\python-shooter.org-api>SubFinder.py "F:\迅雷下载\The Walking Dead" -r
Find 8 videos

行尸走肉.第六季.The.Walking.Dead.S06E05.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.chn.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn.srt
行尸走肉.第六季.The.Walking.Dead.S06E05.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.eng.srt
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn2.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng.srt
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng2.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng2.ass
********************************************************************************
Finish.find 32 subtitles,32 sucessed,0 failed,2 files not found subtitle
Can't found following video file's subtitles:
  行尸走肉.第六季.The.Walking.Dead.S06E06.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.mp4
  行尸走肉.第六季.The.Walking.Dead.S06E02.2015.HD720P.X264.AAC.English.CHS-ENG.Mp4Ba.mp4
```

- 递归下载并压缩打包
```bash
F:\WorkFile\github\python-shooter.org-api>SubFinder.py "F:\迅雷下载\The Walking Dead" -r -c
Find 8 videos

行尸走肉.第六季.The.Walking.Dead.S06E05.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.chn.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn.srt
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn.srt
行尸走肉.第六季.The.Walking.Dead.S06E05.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.eng.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.chn2.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng.ass
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng.srt
The.Walking.Dead.S06E03.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E08.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E07.720p.HDTV.x264-FLEET.eng2.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.chn.srt
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.chn2.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng.ass
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng2.ass
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E04.PROPER.720p.HDTV.x264-KILLERS.eng.srt
The.Walking.Dead.S06E01.PROPER.720p.HDTV.x264-KILLERS.eng2.ass
********************************************************************************
subtitles.zip saving in F:\迅雷下载\The Walking Dead\subtitles
********************************************************************************
Finish.find 32 subtitles,32 sucessed,0 failed,2 files not found subtitle
Can't found following video file's subtitles:
  行尸走肉.第六季.The.Walking.Dead.S06E06.2015.HD1080P.X264.AAC.English.CHS-ENG.Mp4Ba.mp4
  行尸走肉.第六季.The.Walking.Dead.S06E02.2015.HD720P.X264.AAC.English.CHS-ENG.Mp4Ba.mp4

```
