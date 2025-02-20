#!/usr/bin/env python3
import argparse
from lib.common import AppException,InputBase,Settings
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
        in_langs = self.in_data_arr[0].subtitles.keys() #入力ファイルの言語リスト

        #入力ファイルの言語リストと、"translate_langs"の言語リストの差分のリスト＝翻訳を追加する言語リストを作成
        trans_langs = []
        for lang in Settings.api()["translate_langs"]:
            if not lang in in_langs:
                trans_langs.append(lang)

        #原文のリストを作成
        org_lang = Settings.api()["org_lang"]
        set_org = set([data.subtitles[org_lang] for data in self.in_data_arr])
        
        #翻訳
        tl = Translate()
        dic = tl.make_dict(org_lang,trans_langs,set_org)
        
        #訳を追加
        for data in self.in_data_arr:
            org = data.subtitles[org_lang]  #原文
            subtitles_new = {org_lang:org}
            for lang in Settings.api()["translate_langs"]:
                if lang in data.subtitles.keys():
                    #すでにある訳文を使用
                    subtitles_new[lang]=data.subtitles[lang]
                else:
                    #今回翻訳した訳文
                    subtitles_new[lang]=dic[org][lang]
            data.subtitles = subtitles_new

        #excelファイル出力
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file'       ,help="入力excelファイル")    
    parser.add_argument('out_excel_file'      ,help="出力excelファイル")

    args = parser.parse_args()
    print(f"引数：{args}")

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)
