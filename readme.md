# subtitletools

原文のファイルから、対訳が付いた字幕ファイルを作成する。自動翻訳サイトを使用する。  
使用している翻訳サイト：  
みんなの自動翻訳  

```url
https://mt-auto-minhon-mlt.ucri.jgn-x.jp/  
```

SRT形式の字幕ファイルを作成する。直接SRT形式で作成するのは面倒。入力しやすいようにexcelで入力する。excelファイルの形式はinput形式と呼ぶ。input形式からSRT形式ファイルに変換する。  

## 設定

### config/api.jsonc

サンプルファイルはconfig/sample/api.jsonc  
サンプルファイルをコピーして値を修正する  
みんなの自動翻訳のapiを使用するための情報を設定する。  

|項目名|内容|
|:-|:-|
|NAME|ログイン名|
|KEY|ログインして調べる|  
|SECRET|ログインして調べる|

### data/ディレクトリを作成

launch-script.pyを使う場合に必要  
launch-script.pyで参照する  
入出力ファイルを置くディレクトリ

### config/launch_settings.jsonc

launch-script.pyを使う場合に必要  
launch-script.pyで参照する  
サンプルファイルはconfig/sample/launch_settings.jsonc  
サンプルファイルをコピーし、必要なら修正する

## 作業の流れ

1. 原文ファイル（org.txt）を作成
2. org2input.pyでorg.txtから入力用excelファイル(input.xlsx)を作成
3. input.xlsxに字幕毎の開始秒、終了秒を記入
4. input2srt.pyでinput.xlsxからSRT形式の字幕ファイル(srt.txt)を作成

## スクリプト

### launch-script.py

各スクリプトを選択して起動するGUIプログラム  
入出力ファイルはdata/ディレクトリを作成してそこに置く

### org2input.py

原文ファイルから、excelのinput形式ファイルを作成する。翻訳を追加する。
このinput形式に開始秒を入力してから、SRT形式ファイルに変換する。  

```text
usage: trans2input.py [-h] in_file out_excel_file

positional arguments:
  in_file         原文ファイル
  out_excel_file  出力excelファイル。input形式
```

### trans2input.py

事前に、youtubeの文字起こしをファイルにコピーしておく。このファイルを文字起こしファイルと呼ぶ  
文字起こしファイルから、excelのinput形式ファイルを作成する。翻訳を追加する。  

```text
usage: trans2input.py [-h] in_file out_excel_file

positional arguments:
  in_file         文字起こしファイル
  out_excel_file  出力excelファイル。input形式
```

### input2srt.py

excelのinput形式→SRT形式ファイルに変換

```text
usage: input2srt.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力SRT形式ファイル

options:
  -h, --help            show this help message and exit
  --subtitle_langs SUBTITLE_LANGS
                        出力する言語。カンマ区切りのリスト。省略時はexcelの言語をすべて出力する
```

### input2txt.py

excelのinput形式→テキスト形式に変換

```text
usage: input2txt.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力ファイル
```

### input2tag.py

excelのinput形式→mp3のlyricsタグ形式に変換

```text
usage: input2tag.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力ファイル
```

### srt2input.py

SRT形式ファイル→excelのinput形式ファイルに変換  
連番は無視して1から振り直す  
開始/終了秒で秒以下は無視  
字幕文字列は１行が一つの言語に対応する  

```text
usage: srt2input.py [-h] [--subtitle_langs SUBTITLE_LANGS] in_file out_excel_file

positional arguments:
  in_file         入力SRTファイル
  out_excel_file  出力excelファイル
  subtitle_langs SUBTITLE_LANGS
                  入力SRTファイルの言語のリスト。カンマ区切り

options:
  -h, --help            show this help message and exit
```

### srt2vtt.py

srt形式からvtt形式に変換

```text
usage: srt2vtt.py [-h] in_file out_file

positional arguments:
  in_file     入力SRT形式ファイル
  out_file    出力VTT形式ファイル

options:
  -h, --help  show this help message and exit
```

### addsec2input.py

input形式の中の開始秒、終了秒に指定秒を加える  

```text
usage: addsec2input.py [-h] [--start_sec START_SEC] [--end_sec END_SEC] in_excel_file out_excel_file addorsub sec

positional arguments:
  in_excel_file         入力excelファイル
  out_excel_file        出力excelファイル
  addorsub              add:足す/sub:引く
  sec                   加減する秒数（hh:mm:ss）

options:
  -h, --help            show this help message and exit
  --start_sec START_SEC
                        書き換える秒数の、開始秒数（hh:mm:ss）。この秒数以後の時間を書き換える
  --end_sec END_SEC     書き換える秒数の、終了秒数（hh:mm:ss）。この秒数以前の時間を書き換える
```

### addlang2input.py

input形式excelファイルに、翻訳した言語の列を追加  
config/api.jsonの"translate_langs"の言語の中で、input.xlsxに無い言語があれば、その言語の列を追加する  
追加した列に翻訳を入れる  

```text
usage: addlang2input.py [-h] in_excel_file out_excel_file

positional arguments:
  in_excel_file   入力excelファイル
  out_excel_file  出力excelファイル
```

### fill-input.py

input形式excelファイルの、翻訳が抜けている箇所に翻訳を追加する

```text
positional arguments:
  in_excel_file   入力excelファイル
  out_excel_file  出力excelファイル
```

## 各ファイルの形式

ファイルのエンコーディングはUTF-8  

### 原文ファイル

原文が入っているテキストファイル
形式：文字列、改行  

### 文字起こしファイル

youtubeの文字起こしからコピーできる  
形式：開始秒(mm:ss)、改行、文字列

```text
00:00
文字列1
00:10
文字列2
```

### input形式

excelファイル。

| s_hour | s_min | s_sec | e_hour | e_min | e_sec | 言語 |  
| --- | --- | --- | --- | --- | --- | --- |
| 開始時(hh) | 開始分(mm) | 開始秒(ss) | 終了時(hh) | 終了分(mm) | 終了秒(ss) | 文章 |  

開始/終了＋時/分/秒は字幕を表示するタイミング  
最初の行は、開始時を省略した場合は0とする。開始分は省略できない  
開始時/分を省略した行は、前行以前の開始時/分を開始時/分とする  
終了時/分/秒を全て省略した行は、次の行の開始時/分/秒を終了時/分/秒とする。最終行は終了時/分/秒を省略できない  
終了時/分のみ省略した場合、開始時/分を終了時/分とする  

### SRT形式

一般的な字幕フォーマット。youtube、VLCメディアプレイヤー、penguin subtitle playerなどで使える。  
形式：通番、開始秒(hh:mm:ss,000)-->終了秒、文字列、改行区切り  

```text
1
00:00:00,000 --> 00:00:00,000
文字列1
文字列2

2
00:00:00,000 --> 00:00:00,000
文字列1
文字列2
```

### VTT形式

一般的な字幕フォーマット。youtube、VLCメディアプレイヤー、penguin subtitle playerなどで使える。  
形式：通番、開始秒(hh:mm:ss.000)-->終了秒、文字列、改行区切り  
連番は無くてもOK。無視される

```text
WEBVTT

1
00:00:00.000 --> 00:00:00.000
文字列1
文字列2

2
00:00:00,000 --> 00:00:00,000
文字列1
文字列2
```

### テキスト形式

ブログにのせる訳文テキスト用  
形式：開始秒(mm:ss)、文字列

```text
00:00
文字列1
文字列2
```

### mp3のlyricsタグ形式

形式：開始秒([hh:mm:ss.000])、文字列  

```text
[00:00:05.000]文字列1
[00:00:10.000]文字列2
```
