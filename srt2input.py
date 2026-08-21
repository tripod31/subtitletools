#!/usr/bin/env python3
import argparse
import os
import sys
from lib.common import InputBase,SrtUtil,print_args,AppException

"""
SRT形式ファイルからinput形式excelファイルに変換
"""

class Process(InputBase):
    def __init__(self):
        super().__init__()
    
    def main(self):
        self.in_data_arr = SrtUtil.read_file(args.in_file,args.subtitle_langs)
        super().out_excel(args.out_excel_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'       ,help="入力SRTファイル")    
    parser.add_argument('out_excel_file',help="出力excelファイル")
    parser.add_argument('--subtitle_langs',
                        help="入力SRTファイルの言語のリスト。カンマ区切り。省略時はL1,L2…とする"
                        )
        
    args = parser.parse_args()
    print_args(args)
    if os.path.exists(args.out_excel_file):
        ans = input(f"{args.out_excel_file}：上書きしますか？(Yes:y)")
        if ans != 'y':
            sys.exit()

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)