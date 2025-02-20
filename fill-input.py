#!/usr/bin/env python3
import argparse
from lib.common import AppException,Settings
from lib.translate import Translate
import pandas

"""
input形式excelファイルの、翻訳が抜けている箇所に翻訳を追加する
開始秒は未入力でOK
"""

class Process():
    #開始秒が未入力のため、InputBaseクラスは継承しない

    def __init__(self):
        pass
    
    def main(self):
        #excelファイル読み込み
        df = pandas.read_excel(args.in_excel_file,header=0)

        in_langs = list(df.columns.values[6:])    #入力ファイルのヘッダーから、言語のリストを取得
        org_lang = Settings.api["org_lang"]
        in_langs.remove(org_lang)  #翻訳先言語のリスト
        tl = Translate(args.test)

        #翻訳対象の辞書を作成
        dic_in = {}
        for idx,row in df.iterrows():
            org = row[org_lang]
            if pandas.isnull(org):
                continue
            for lang in in_langs:
                if pandas.isnull(row[lang]):
                    if not org in dic_in.keys():
                        dic_in[org] = {}         
                    dic_in[org][lang]=None

        if len(dic_in.keys())==0:
            print("翻訳が抜けている箇所はありません")
            return

        #翻訳
        dic = tl.make_dict(org_lang,dic_in)

        #翻訳が抜けている箇所に翻訳を追加
        for idx,row in df.iterrows():
            for lang in in_langs:        
                if not pandas.isnull(row[org_lang]) and pandas.isnull(row[lang]):
                    org = row[org_lang]
                    df.at[idx,lang] = dic[org][lang]
       
        #excelファイル出力
        df.to_excel(args.out_excel_file,index=False)
        print(f"出力しました：{args.out_excel_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file'       ,help="入力excelファイル")    
    parser.add_argument('out_excel_file'      ,help="出力excelファイル")
    parser.add_argument('--test',
                        action="store_true",
                        help='テスト用。APIでの翻訳を行わない')
    args = parser.parse_args()
    print(f"引数：{args}")

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)
