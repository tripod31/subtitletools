# subtitletools

原文のファイルから、対訳ファイルを作成する。自動翻訳サイトを使用する。  
使用している翻訳サイト：  
みんなの自動翻訳  
https://mt-auto-minhon-mlt.ucri.jgn-x.jp/  
SRT形式の字幕ファイルを作成する。直接SRT形式で作成するのは面倒。入力しやすいようにexcelで入力する。excelファイルの形式はinput形式と呼ぶ。input形式からSRT形式ファイルに変換する。  

## 設定
### config/api.jsonc
サンプルファイルはconfig/api.jsonc.sample  
サンプルファイルをコピーして値を修正する  
みんなの自動翻訳のapiを使用するための情報を設定する。  
| 項目名 | 内容 |  
| --- | --- |  
| API_PARAM_JP | 日本語訳に使用するAPI |  
| API_PARAM_ENG | 英語訳に使用するAPI |  
| NAME | ログイン名 |  
| KEY  | ログインして調べる |  
| SECRET | ログインして調べる |   

### data/ディレクトリを作成
launch-script.pyを使う場合に必要  
launch-script.pyで参照する  
入出力ファイルを置くディレクトリ

### config/launch_settings.jsonc
launch-script.pyを使う場合に必要  
launch-script.pyで参照する  
サンプルファイルはconfig/api.jsonc.sample  
サンプルファイルをコピーし、必要なら修正する

## 作業の流れ
1. 原文ファイルを作成
2. org2input.pyで入力用excelファイル(input.xlsx)を作成
3. input.xlsxに歌詞毎の開始秒、終了秒を記入
4. input2srt.pyでSRT形式の字幕ファイル(srt.txt)を作成

## スクリプト
### launch-script.py
各スクリプトを選択して起動するGUIプログラム  
入出力ファイルはdata/ディレクトリを作成してそこに置く

### org2input.py
原文ファイルから、excelのinput形式ファイルを作成する。翻訳を追加する。    
このinput形式に開始秒を入力してから、SRT形式ファイルに変換する。  
```
usage: trans2input.py [-h] in_file out_excel_file

positional arguments:
  in_file         原文ファイル
  out_excel_file  出力excelファイル。input形式
```

### trans2input.py
事前に、youtubeの文字起こしをファイルにコピーしておく。このファイルを文字起こしファイルと呼ぶ  
文字起こしファイルから、excelのinput形式ファイルを作成する。翻訳を追加する。  
```
usage: trans2input.py [-h] in_file out_excel_file

positional arguments:
  in_file         文字起こしファイル
  out_excel_file  出力excelファイル。input形式
```
### input2srt.py
excelのinput形式→SRT形式ファイルに変換
```
usage: input2srt.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力SRT形式ファイル
```

### input2txt.py
excelのinput形式→テキスト形式に変換
```
usage: input2txt.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力ファイル
```
### input2tag.py
excelのinput形式→mp3のlyricsタグ形式に変換
```
usage: input2tag.py [-h] in_excel_file out_file

positional arguments:
  in_excel_file  入力excelファイル
  out_file       出力ファイル
```

### srt2input.py
SRT形式ファイル→excelのinput形式ファイルに変換  
```
usage: srt2input.py [-h] in_file out_excel_file

positional arguments:
  in_file         入力SRTファイル
  out_excel_file  出力excelファイル
```
### addsec2input.py
input形式の中の開始秒、終了秒に指定秒を加える  
```
usage: addsec2input.py [-h] [--start_sec START_SEC] [--end_sec END_SEC] in_excel_file out_excel_file add_sec

positional arguments:
  in_excel_file         入力excelファイル
  out_excel_file        出力excelファイル
  add_sec               足す加減する秒数（[+-]mm:ss）

options:
  -h, --help            show this help message and exit
  --start_sec START_SEC
                        書き換える秒数の、開始秒数（mm:ss）。この秒数以後の時間を書き換える
  --end_sec END_SEC     書き換える秒数の、終了秒数（mm:ss）。この秒数以前の時間を書き換える
```

## 各ファイルの形式
ファイルのエンコーディングはUTF-8  
### 原文ファイル
原文が入っているテキストファイル
形式：文字列、改行  

### 文字起こしファイル
youtubeの文字起こしからコピーできる  
形式：開始秒(mm:ss)、改行、文字列
```
00:00
文字列1
00:10
文字列2
```

### input形式
excelファイル。
| s_min | s_sec | e_min | e_sec | org | eng | jp |  
| --- | --- | --- | --- | --- | --- | --- |  
| 開始分(mm) | 開始秒(ss) | 終了分(mm) | 終了秒(ss) | 原文 | 英訳 | 日本語訳 |  

開始/終了+分/秒は字幕を表示するタイミング  
開始分を省略した行は、前行以前の開始分を開始分とする。最初の行は開始分を省略できない。  
終了分/秒を省略した行は、次の行の開始分/秒を終了分/秒とする。最終行は終了分/秒を省略できない。  

分、秒は整数  
### SRT形式
一般的な字幕フォーマット。youtube、VLCメディアプレイヤー、penguin subtitle playerなどで使える。  
形式：通番、開始秒(hh:mm:ss.000)-->終了秒、文字列、改行区切り  
```
1
00:00:00,000 --> 00:00:00,000
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
```
00:00
文字列1
文字列2
```
### mp3のlyricsタグ形式
形式：開始秒([mm:ss.000])、文字列  
```
[00:05.000]文字列1
[00:10.000]文字列2
```
