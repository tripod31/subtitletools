#!/usr/bin/env python3

"""
input形式からSRT形式の字幕ファイルを出力
"""

import argparse
import os
import sys
from lib.common import AppException,InputBase,print_args

class Process(InputBase):

    def __init__(self):
        super().__init__()

    def out_file(self):
        """
        InputDataの配列をファイルに出力
        InputBase.excel2fileから呼ばれる
        """
        lines = []
        with open(args.out_file,"w",encoding='utf-8') as f:
            for data in self.in_data_arr:
                if self.subtitle_langs is not None:
                    lines.extend( data.to_srt(self.subtitle_langs))
                else:
                    lines.extend( data.to_srt())
                lines.append("")
            f.write("\n".join(lines))
            f.write("\n") #最後に空の行を出力しないと、最後の歌詞がpenguin subtitle playerで表示されない？
        print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file' ,help="入力excelファイル")    
    parser.add_argument('out_file'      ,help="出力SRT形式ファイル") 
    parser.add_argument('--subtitle_langs'
                        ,help="出力する言語。カンマ区切りのリスト。省略時はexcelの言語をすべて出力する") 
    
    args = parser.parse_args()
    print_args(args)
    
    if os.path.exists(args.out_file):
        ans = input(f"{args.out_file}：上書きしますか？(Yes:y)")
        if ans != 'y':
            print("中止します")
            sys.exit()

    proc = Process()  
    try:
        proc.excel2file(args)
    except AppException as e:
        print(e)