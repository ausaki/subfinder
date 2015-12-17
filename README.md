## 利用shooter.org提供的api下载字幕

** API: https://www.shooter.cn/api/subapi.php **

api使用说明请参考原文: [射手字幕网api使用说明](https://docs.google.com/document/d/1ufdzy6jbornkXxsD-OGl3kgWa4P9WO5NZb6_QYZiGI0/preview)

## 使用方法
该脚本可以找出给定目录下的所有视频文件(`注意: 不递归子目录`), 然后利用api下载所有
匹配的中英文字幕。也可以只下载单个视频对应的字幕.
- -o, --output 指定字幕保存目录,默认为path(即视频文件所在的目录).
- -c, --compress 指定是否要压缩字幕,对下载单个视频的字幕无效.
- -n, --threads 指定线程数,不能超过目录包含的总视频文件数目.
- --lang 选择字幕语言, 可选值有:[Chn, Eng], 默认为[Chn,Eng]

```
# example1 下载单个视频的字幕
$ SubFinder.py "F:\迅雷下载\fargoS01\Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.mkv"
Find 1 video

Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt


********************************************************************************
Finish.find 6 subtitles,6 sucessed,0 failed,0 files not found subtitle

# example2 下载目录中所有视频的字幕
$ SubFinder.py F:\迅雷下载\fargoS01
Find 10 videos

Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Chn2.ass
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Chn3.srt
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E04.Eating.the.Blame.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E01.The.Crocodile's.Dilemma.720p.WEB-DL.DD5.1.H.264-BS.Eng2.ass
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E07.Who.Shaves.the.Barber.720p.WEB-DL.DD5.1.H.264-BS.Eng3.srt
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Chn3.srt
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E02.The.Rooster.Prince.720p.WEB-DL.DD5.1.H.264-BS.Eng3.srt
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E05.The.Six.Ungraspables.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Chn3.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E03.A.Muddy.Road.720p.WEB-DL.DD5.1.H.264-BS.Eng3.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Chn2.srt
Fargo.S01E08.The.Heap.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E06.Buridan's.Ass.720p.WEB-DL.DD5.1.H.264-BS.Eng2.srt
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Chn2.ass
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E09.A.Fox.a.Rabbit.and.a.Cabbage.720p.WEB-DL.DD5.1.H.264-BS.Eng2.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Chn.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Chn.srt
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Chn2.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng.ass
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng.srt
Fargo.S01E10.Morton's.Fork.720p.WEB-DL.DD5.1.H.264-BS.Eng2.ass


********************************************************************************
Finish.find 60 subtitles,60 sucessed,0 failed,0 files not found subtitle

```