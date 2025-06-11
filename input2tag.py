#!/usr/bin/env python3
import argparse
from lib.common import AppException,InputBase,format_timedelta,Settings,print_args

"""
input形式からmp3のlyricタグ用テキストファイルを出力
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
                for lang in Settings.api["subtitle_langs"]:
                    lines.append( f"[{format_timedelta(data.start)}.000]{data.subtitles[lang]}")
            f.write("\n".join(lines))
        print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file' ,help="入力excelファイル")    
    parser.add_argument('out_file'      ,help="出力ファイル") 
    
    args = parser.parse_args()
    print_args(args)

    proc = Process()  
    try:
        proc.excel2file(args)
    except AppException as e:
        print(e)