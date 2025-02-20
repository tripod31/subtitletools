import argparse
from lib.translate import Translate
import pandas
from lib.common import InputData

"""
原文ファイルからexcelのinput形式ファイルを作成
訳を追加
"""

class Process:
    def __init__(self):
        pass
        
    def transrate(self):
        with open(args.in_file,encoding='utf-8') as f:
            in_lines = f.readlines()

        set_org = set([line.strip() for line in in_lines]) #重複を除いた原文のリスト
        
        tl = Translate()
        dic = tl.make_dict(set_org)

        out_row = {col:"" for col in InputData.INPUT_COLS}
        rows=[]
        for line in in_lines:
            org = line.strip()
            if len(org)==0:
                continue

            row = out_row.copy()
            row["org"]      = org
            row["eng"]      = dic[org]["eng"]
            row["jp"]       = dic[org]["jp"]
            rows.append(row)

        #excel出力
        df = pandas.DataFrame(rows)
        df.to_excel(args.out_excel_file,index=False)
        print(f"{args.out_excel_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="原文ファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル')
    args = parser.parse_args()
    print(f"引数：{args}")

    proc=Process()
    proc.transrate()