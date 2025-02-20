#!/usr/bin/env python3
import argparse
import re
from datetime import timedelta
from lib.common import AppException,InputBase

"""
input形式excelファイルの秒数に、指定した秒数を加減算
"""

class Process(InputBase):
    def __init__(self):
        super().__init__()
        if args.start_sec is not None:
            m = re.match(r"(\d+):(\d+)",args.start_sec)
            if not m:
                raise AppException(f"start_sec:秒数の形式がmm:ssでない：{args.start_sec}")
            self.start_sec = timedelta(minutes=int(m[1]),seconds=int(m[2]))
        else:
            self.start_sec = None
        
        if args.start_sec is not None:
            m = re.match(r"(\d+):(\d+)",args.end_sec)
            if not m:
                raise AppException(f"end_sec:秒数の形式がmm:ssでない：{args.end_sec}")
            self.end_sec = timedelta(minutes=int(m[1]),seconds=int(m[2]))
        else:
            self.end_sec = None

        m = re.match(r"([+-])(\d+):(\d+)",args.sec)
        if not m:
            raise AppException(f"sec:秒数の形式が[+-]mm:ssでない：{args.sec}")
        self.plus_minus =m[1]
        self.sec = timedelta(minutes=int(m[2]),seconds=int(m[3]))

    def is_in_range(self,time:timedelta)->bool:
        """
        時間が範囲内にあるかを返す。
        引数：
            time:   比較する時間
        """
        ret = True
        if self.start_sec is not None:
            if time < self.start_sec:
                ret = False
        
        if self.end_sec is not None:
            if time > self.end_sec:
                ret =  False  
        return ret
    
    def main(self):
        #excelファイル読み込み
        self.read_excel(args)

        #データ書き換え
        for data in self.in_data_arr:
            if self.is_in_range(data.start):
                if self.plus_minus == "+":
                    data.start += self.sec
                else:
                    data.start -= self.sec
            if self.is_in_range(data.end):
                if self.plus_minus == "+":
                    data.end += self.sec
                else:
                    data.end -= self.sec

        #データチェック
        self.check_data()

        #excelファイル出力
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_excel_file'       ,help="入力excelファイル")    
    parser.add_argument('out_excel_file'      ,help="出力excelファイル")
    parser.add_argument('sec'                 ,help="加減する秒数（[+-]mm:ss）")
    parser.add_argument('--start_sec'
                        ,help="書き換える秒数の、開始秒数（mm:ss）。この秒数以後の時間を書き換える")
    parser.add_argument('--end_sec'
                        ,help="書き換える秒数の、終了秒数（mm:ss）。この秒数以前の時間を書き換える")

    args = parser.parse_args()
    print(f"引数：{args}")

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)
