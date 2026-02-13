#!/usr/bin/env python3
import argparse
import os
import sys
import re
from dataclasses import dataclass,field
from lib.common import InputData,InputBase,print_args,AppException

"""
SRT形式ファイルからinput形式excelファイルに変換
"""

@dataclass
class Block:
    no:int = 0
    s_hour: int =0
    s_min:int =0
    s_sec:int =0
    e_hour:int =0
    e_min:int =0
    e_sec:int =0
    subtitles:list =field(default_factory=list)

class Process(InputBase):
    def __init__(self):
        super().__init__()
        self.re_timespan = re.compile(r"(\d{2}):(\d{2}):(\d{2})[\.,]000 --> (\d{2}):(\d{2}):(\d{2})[\.,]000")
    
    def parse_block(self,lines):
        """
        SRT形式ファイルの１つのブロックをパース
        """
        block = Block()
        #NO行
        if not lines[0].isdigit():
            raise AppException(f"データブロックの最初が番号でない：{lines[0]}")
        block.no = int(lines[0])

        #時間指定行
        m = self.re_timespan.match(lines[1])
        if not m:
            raise AppException(f"データブロックの２行目が時間指定行でない：NO={block.no}：{lines[1]}")
        block.s_hour    = int(m[1])
        block.s_min     = int(m[2])
        block.s_sec     = int(m[3])
        block.e_hour    = int(m[4])
        block.e_min     = int(m[5])
        block.e_sec     = int(m[6])        

        #字幕
        if len(lines)<=2:
            raise AppException(f"データブロックに字幕がない：NO={block.no}")
        block.subtitles=lines[2:]

        return block

    def parse_srt(self):
        """
        SRT形式ファイルをパース
        字幕は改行で区切ってリストで読み込む
        """
        with open(args.in_file,encoding='utf-8') as f:
            lines = f.readlines()

        blocks=[]
        buf =[]
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                # 空行
                if len(buf)>0:
                   block = self.parse_block(buf)
                   blocks.append(block)
                   buf.clear()
            else:
                buf.append(line)
        return blocks
        
    def read_srt(self):
        """
        SRT形式ファイルをInputDataのリストに読み込む
        字幕のリストを{言語：字幕}の辞書に変換
        """

        if args.subtitle_langs is not None:
            subtitle_langs = args.subtitle_langs.split(",")
        
        num_langs = None    #言語の数
        #InputDataのリストに読み込む
        blocks = self.parse_srt()
        for idx,block in enumerate(blocks):
            subtitles  = block.subtitles

            if args.subtitle_langs is not None and len(subtitles)!=len(subtitle_langs):
                raise AppException(f"字幕の行数が指定された言語数と異なる：NO={block.no}")

            #字幕の行数＝言語の数が前のデータと同じかチェック
            if num_langs is None:
                num_langs = len(subtitles)
            else:
                if len(subtitles) != num_langs:
                    raise AppException(f"字幕の行数が前のデータとちがう：NO={block.no}")
            
            dic = {}
            if args.subtitle_langs is not None:
                for idx,lang in enumerate(subtitle_langs):
                    dic[lang] = subtitles[idx]
            else:
                for idx in range(0,num_langs):
                    lang = f"L{idx+1}"
                    dic[lang] = subtitles[idx]

            idata = InputData(
                            index   =block.no,
                            s_hour  =block.s_hour,
                            s_min   =block.s_min,
                            s_sec   =block.s_sec,
                            e_hour  =block.e_hour,
                            e_min   =block.e_min,
                            e_sec   =block.e_sec,
                            subtitles=dic)
            self.in_data_arr.append(idata)

    def main(self):
        self.read_srt()
        self.out_excel(args)

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
            print("中止します")
            sys.exit()

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)