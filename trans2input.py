"""
文字起こしファイルからexcelのinput形式ファイルを作成
翻訳を追加
"""

import argparse
import os
import sys
from dataclasses import dataclass
from lib.translate import Translate
from lib.common import InputBase,TransUtil,Settings,AppException,print_args

class Process(InputBase):
    def __init__(self):
        super().__init__()

    def translate(self):
        """
        配列に翻訳を追加する
        """
        
        #翻訳
        tl = Translate()
        org_lang = Settings.api["org_lang"]
        org_texts = [data.subtitles[Settings.api["org_lang"]] for data in self.in_data_arr]
        for lang in Settings.api["translate_langs"]:
            text = tl.translate("\n".join(org_texts),org_lang,lang)
            texts = text.split("\n")
        
            #訳を配列に追加
            for i,data in enumerate(self.in_data_arr):
                data.subtitles[lang]    = texts[i]
                
    def main(self):
        self.in_data_arr = TransUtil.read_trans(args.in_file)
        if args.translate:
            self.translate()
        self.out_excel(args.out_excel_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="文字起こしファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル。input形式')
    parser.add_argument('--translate',
                        action="store_true",
                        help='翻訳を行う')    
    
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
