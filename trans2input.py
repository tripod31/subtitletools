"""
文字起こしファイルからexcelのinput形式ファイルを作成
翻訳を追加
"""

import argparse
import pyparsing as pp
import os
import sys
import re
from dataclasses import dataclass,field
from lib.translate import Translate
from lib.common import InputData,InputBase,Settings,AppException,print_args

@dataclass
class Block:
    s_min:int =0
    s_sec:int =0
    subtitle:str=""

class Process(InputBase):
    def __init__(self):
        super().__init__()
        self.re_time = re.compile(r"(\d+):(\d+)")

    def parse_block(self,lines):
        """
        文字起こしファイルの１つのブロックをパース
        """
        block = Block()

        #時間指定行
        start = lines[0]
        m = self.re_time.match(lines[0])
        if not m:
            raise AppException(f"データブロックの１行目が時間指定行でない：{lines[0]}")
        start = lines[0]
        block.s_min     = int(m[1])
        block.s_sec     = int(m[2])

        #字幕
        if len(lines)<=1:
            raise AppException(f"データブロックに字幕がない：{start}")
        block.subtitle=" ".join(lines[1:])

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
                continue

            if self.re_time.match(line):
                # 時間指定行
                if len(buf)>0:
                   block = self.parse_block(buf)
                   blocks.append(block)
                   buf.clear()

            buf.append(line)

        return blocks
 
    def read_file(self):
        """
        文字起こしファイルをInputDataの配列に読み込む
        """
        with open(args.in_file,encoding='utf-8') as f:
            block = f.read()

        blocks = self.parse_srt()

        #InputDataのリストに読み込む
        for idx,block in enumerate(blocks):
            s_min   = block.s_min
            s_sec   = block.s_sec
            subtitles = {Settings.api["org_lang"]:block.subtitle}
            for lang in Settings.api["translate_langs"]:
                subtitles[lang]=""
            block = InputData(index=idx+1,
                             s_hour=0,s_min=s_min,s_sec=s_sec,
                             #終了秒には0:0:0を入れておく。excel出力時はnanに変換する（InputBase.out_excel）
                             e_hour=0,e_min=0,e_sec=0,   
                             subtitles=subtitles)
            self.in_data_arr.append(block)

    def translate(self):
        """
        InputDataに翻訳を追加する
        """
        #翻訳辞書を準備
        dic_in = {}
        org_lang = Settings.api["org_lang"]
        for data in self.in_data_arr:
            org = data.subtitles[org_lang]
            dic_in[org] =Settings.api["translate_langs"].copy()

        #翻訳
        tl = Translate(args.test)
        dic=tl.make_dict(org_lang,dic_in)

        #訳を追加
        for data in self.in_data_arr:
            org = data.subtitles[org_lang]
            for lang in Settings.api["translate_langs"]:
                data.subtitles[lang]    = dic[org][lang]
                
    def main(self):
        self.read_file()
        if not args.no_trans:
            self.translate()
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="文字起こしファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル。input形式')
    parser.add_argument('--no_trans',
                        action="store_true",
                        help='翻訳を行わない')    
    parser.add_argument('--test',
                        action="store_true",
                        help='テスト用。TranslateクラスでAPIでの翻訳を行わない')   
    
    args = parser.parse_args()
    print_args(args)

    if os.path.exists(args.out_excel_file):
        ans = input(f"{args.out_excel_file}：上書きしますか？(Yes:y)")
        if ans != 'y':
            sys.exit()

    proc=Process()
    try:
        proc.main()
    except AppException as e:
        print(e)
