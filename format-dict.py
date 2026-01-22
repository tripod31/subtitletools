#!/usr/bin/env python3
import argparse
import pandas
import math
import openpyxl
from openpyxl.worksheet.pagebreak import Break
from lib.common import print_args

"""
辞書csvを読み込む
少ないページ数に印刷するために折りたたんでexcel出力
"""

class Process:
    def __init__(self,args):
        self.args = args
        self.cols_num = int(args.cols_num)
        self.rows_num = int(args.rows_num)

    def main(self):
        #入力CSV読み込み
        df = pandas.read_csv(
                self.args.in_file,
                header=None
                )
        in_arr = df.to_numpy().tolist()
        
        #出力用の２次元配列を作成。データは空文字
        out_arr = []
        nums_per_page = self.rows_num*self.cols_num     #ページ内のデータ数
        pages = math.ceil(len(in_arr) / nums_per_page)
        rows_num = pages * self.rows_num
        for i in range(0,rows_num):
            out_arr.append([""]*self.cols_num*2)
        
        #出力用配列にデータを入れる
        for i,row in enumerate(in_arr):
            page_index = int (i / nums_per_page)        #ページのインデックス
            index = i % (nums_per_page)                 #ページ内でのデータのインデックス
            row_idx =  (page_index*self.rows_num) + (index % self.rows_num)
            col_idx = int(index / self.rows_num)
            org_word = row[0]
            to_word = row[1]
            out_arr[row_idx][col_idx*2]=org_word
            out_arr[row_idx][col_idx*2+1]=to_word

        self.out_excel(out_arr)

    def out_excel(self,out_arr):
        #excel出力
        wb = openpyxl.Workbook()
        ws = wb["Sheet"]

        for row_idx,row in enumerate(out_arr):
            for col_idx,val in enumerate(row):
                col_letter = chr(ord("A")+col_idx)
                address = f"{col_letter}{row_idx+1}"
                ws[address] = val
                if row_idx >0 and ((row_idx) % self.rows_num == 0):
                    #改ページ
                    ws.row_breaks.append(Break(id=row_idx)) 
        
        wb.save(self.args.out_file)
        print(f"{self.args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="入力する辞書ファイル")    
    parser.add_argument('out_excel_file'    ,help="出力するexcelファイル")
    parser.add_argument('cols_num'  ,help="列数＠ページ")
    parser.add_argument('rows_num'  ,help="行数＠ページ")

    args = parser.parse_args()
    print_args(args)

    proc = Process(args)
    proc.main()
