#!/usr/bin/env python3
import argparse
from lib.common import AppException,InputBase,Settings,print_args
from lib.translate import Translate

"""
input形式excelファイルに、翻訳した言語の列を追加
config/api.jsonの"translate_langs"の言語の中で、input.xlsxに無い言語があれば、その言語の列を追加する
追加した列に翻訳を入れる
"""

class Process(InputBase):
    def __init__(self):
        super().__init__()
    
    def main(self):
        #excelファイル読み込み
        self.read_excel(args)
        in_langs = self.in_data_arr[0].subtitles.keys() #入力ファイルの１番目のデータから、言語のリストを取得

        #入力ファイルの言語リストと、"translate_langs"の言語リストの差分のリスト＝翻訳を追加する言語リストを作成
        trans_langs = []
        for lang in Settings.api["translate_langs"]:
            if not lang in in_langs:
                trans_langs.append(lang)
      
        #翻訳辞書を準備
        dic_in = {}
        org_lang = Settings.api["org_lang"]
        for data in self.in_data_arr:
            org = data.subtitles[org_lang]
            dic[org] =Settings.api["translate_langs"].copy()

        #翻訳
        tl = Translate(args.test)
        dic=tl.make_dict(org_lang,dic_in)
        
        #訳を追加
        for data in self.in_data_arr:
            org = data.subtitles[org_lang]  #原文
            subtitles_new = data.subtitles.copy()
            for lang in dic[org]:
                subtitles_new[lang]=dic[org][lang]
            data.subtitles = subtitles_new

        #excelファイル出力
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file'       ,help="入力excelファイル")    
    parser.add_argument('out_excel_file'      ,help="出力excelファイル")
    parser.add_argument('--test',
                        action="store_true",
                        help='テスト用。APIでの翻訳を行わない')
    args = parser.parse_args()
    print_args(args)

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)
