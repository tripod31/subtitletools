#!/usr/bin/env python3
import argparse
from lib.common import AppException,InputBase,Settings,print_args

"""
input形式からSRT形式の字幕ファイルを出力
"""

class Process(InputBase):

    def __init__(self):
        super().__init__()
        if args.subtitle_langs is None:
            self.subtitle_langs = Settings.api["subtitle_langs"]
        else:
            self.subtitle_langs = args.subtitle_langs.split(",")

    def out_file(self):
        """
        InputDataの配列をファイルに出力
        InputBase.excel2fileから呼ばれる
        """
        lines = []
        with open(args.out_file,"w",encoding='utf-8') as f:
            for data in self.in_data_arr:
                lines.extend( data.to_srt(self.subtitle_langs))
                lines.append("")
            f.write("\n".join(lines))
            f.write("\n") #最後に空の行を出力しないと、最後の歌詞がpenguin subtitle playerで表示されない？
        print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file' ,help="入力excelファイル")    
    parser.add_argument('out_file'      ,help="出力SRT形式ファイル") 
    parser.add_argument('--subtitle_langs'      ,help="出力する言語。カンマ区切りのリスト") 
    
    args = parser.parse_args()
    print_args(args)

    proc = Process()  
    try:
        proc.excel2file(args)
    except AppException as e:
        print(e)