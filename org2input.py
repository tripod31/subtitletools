import argparse
import pandas
import os
import sys
from lib.translate import Translate
from lib.common import Settings,AppException,TIME_COLUMNS,print_args,df2excel

"""
原文からexcelのinput形式ファイルを作成
翻訳を追加
"""

class Process():
    #開始秒が未入力のため、InputBaseクラスは継承しない

    def __init__(self):
        self.rows=[]

    def read_file(self):
        """
        原文ファイルを配列に読み込む
        """
        lines=[]
        with open(args.in_file,encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if len(line)>0:
                    #空行は除く
                    lines.append(line)

        org_lang = Settings.api["org_lang"]
        columns = TIME_COLUMNS + [org_lang] + Settings.api["translate_langs"]
        for line in lines:
            row = {col:"" for col in columns}
            row[org_lang] = line
            self.rows.append(row)

    def translate(self):
        """
        InputDataに翻訳を追加する
        """
        #翻訳辞書を準備
        dic_in = {}
        org_lang = Settings.api["org_lang"]
        for row in self.rows:
            org = row[org_lang]
            dic_in[org] = Settings.api["translate_langs"].copy()

        #翻訳
        tl = Translate(args.test)
        dic = tl.make_dict(org_lang,dic_in)

        #訳を追加
        for row in self.rows:
            org = row[org_lang]
            for lang in Settings.api["translate_langs"]:
                row[lang]    = dic[org][lang]
   
    def main(self):
        self.read_file()
        if not args.no_trans:
            self.translate()

        df = pandas.DataFrame(self.rows)
        df2excel(df,args.out_excel_file)
        print(f"出力しました：{args.out_excel_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="原文ファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル。input形式')
    parser.add_argument('--no_trans',
                        action="store_true",
                        help='翻訳を行わない')
    parser.add_argument('--test',
                        action="store_true",
                        help='テスト用。翻訳でAPIを呼び出さない')
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
        
