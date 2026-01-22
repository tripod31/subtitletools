#!/usr/bin/env python3
import argparse
from lib.common import AppException,InputBase,format_timedelta,Settings,print_args

"""
input形式からブログ用のテキストファイルを出力
"""

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
                lines.append( f"{format_timedelta(data.start)[3:]}")
                if self.subtitle_langs is not None:
                    for lang in self.subtitle_langs:
                        lines.append( f"{data.subtitles[lang]}")
                else:
                    lines.extend(data.subtitles.values())
                lines.append("")
            f.write("\n".join(lines))
        print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file' ,help="入力excelファイル")    
    parser.add_argument('out_file'      ,help="出力ファイル") 
    parser.add_argument('--subtitle_langs'
                        ,help="出力する言語。カンマ区切りのリスト。省略時はexcelの言語をすべて出力する") 
        
    args = parser.parse_args()
    print_args(args)

    proc = Process()  
    try:
        proc.excel2file(args)
    except AppException as e:
        print(e)