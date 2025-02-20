from datetime import timedelta
from collections import namedtuple
import pandas
import math
import numpy as np
import re
import json

class InputData:
    INPUT_COLS = ["s_min","s_sec","e_min","e_sec","org","eng","jp"] #入力用excelファイルの列名
    Input_cols_no = namedtuple("INPUT_COLS_IDX",INPUT_COLS)
    #input_cols_index.列名 = excelの列番号
    input_cols_no = Input_cols_no(**{col:idx+1 for idx,col in enumerate(INPUT_COLS)}) 

    def __init__(self,index:int,s_min:int,s_sec:int,e_min:int,e_sec:int,org:str,eng:str,jp:str):
        self.index       = index
        self.start       = timedelta(minutes=s_min,seconds=s_sec)
        self.end         = timedelta(minutes=e_min,seconds=e_sec)
        self.org = org
        self.eng = eng
        self.jp =jp

    def to_srt(self)->list:
        """
        戻り値：
            SRT形式の文字列の配列
        """
        ret =[]
        ret.append(f"{self.index}") #通し番号
        line_time = f"00:{format_timedelta(self.start)},000 --> 00:{format_timedelta(self.end)},000"
        ret.append(line_time)
        ret.append(self.org)
        if type(self.jp)==str:
            ret.append(self.jp)
        return ret
    
    def to_dict(self)->dict:
        """
        戻り値：
            excel出力用のdict
            indexは出力しない
        """
        data = {col:"" for col in self.INPUT_COLS}
        data["s_min"]   = int(self.start.seconds/60)
        data["s_sec"]   = int(self.start.seconds % 60)
        data["e_min"]   = int(self.end.seconds/60)
        data["e_sec"]   = int(self.end.seconds % 60)
        data["org"]     =self.org
        data["eng"]     =self.eng
        data["jp"]      =self.jp
        return data

class InputBase():
    """
    InputDataを操作する
    """

    def __init__(self):
        self.in_data_arr=[] #InputDataのリスト
        self.prev_s_min = 0 #前回読み込んだ行のs_minを保存

    def read_excel(self,args):
        #excelファイル読み込み
        df = pandas.read_excel(args.in_excel_file,header=0)
        for idx in range(0,df.shape[0]):
            self.read_row(df,idx)

    def read_row(self,df:pandas.DataFrame,idx):
        """
        Excelから読み込んだDaraFrame一行分をInputDataオブジェクトに読み込む
        ルール：
        １行目にs_minが無ければエラー
        s_minが無ければ前の行以前に読み込んだs_minをs_minとする
        endが無ければ一つ後の行の開始秒をendとする
        最終行にendが無ければエラー
        """
        row = df.loc[idx]

        s_min   = row["s_min"]
        s_sec   = row["s_sec"]
        e_min   = row["e_min"]
        e_sec   = row["e_sec"]
        org     = row['org']
        jp      = row['jp']
        eng     = row["eng"]

        if math.isnan(s_min):
            #s_minがない場合
            if idx ==0:
                raise AppException("１行目にs_secがありません")
            s_min = self.prev_s_min #前回読み込んだs_minをs_minとする

        if math.isnan(s_sec):
            raise AppException(f"{idx+1}行目：s_secがありません")

        if math.isnan(e_min):
            if idx >= df.shape[0]-1:
                raise AppException(f"{idx+1}行目：最終行にendがありません")
            #次の行のstartをendとする
            next_row = df.loc[idx+1]
            if not np.isnan(next_row["s_min"]):
                e_min = int(next_row["s_min"])
            else:
                e_min = s_min
            e_sec = int(next_row["s_sec"])           

        self.prev_s_min = s_min #読み込んだs_minを保存
        data = InputData(idx+1,s_min=int(s_min),s_sec=int(s_sec),
                         e_min=int(e_min),e_sec=int(e_sec),org = org,eng=eng,jp=jp)
        self.in_data_arr.append(data)

    def check_data(self):
        """
        InputDataのリストをチェック
        """
        #開始秒チェック
        for idx,data in enumerate(self.in_data_arr):
            #チェック：開始秒=<終了秒
            if not data.start<=data.end:
                raise AppException(f"{idx+1}件目：開始秒＜＝終了秒になっていません")
            #チェック：開始秒>=前件の終了秒
            if idx==0:
                continue
            prev_data = self.in_data_arr[idx-1]
            if not data.start>=prev_data.end:
                raise AppException(f"{idx+1}件目：開始秒＞＝前件の終了秒になっていません")
            
    def out_file(self):
        """
        InputDataのリストをファイルに出力
        子クラスで実装
        """
        pass
    
    def out_excel(self,args):
        """
        InputDataのリストをexcelのinputData形式ファイルに出力
        開始秒が前のデータの終了秒と同じ場合、前のデータの終了秒はnanを入れる
        s_minが前のデータのs_minと同じ場合、s_minにはnanを入れる
        """
        rows = []
        for idx,data in enumerate(self.in_data_arr):
            row = data.to_dict()
            if idx >0:
                prev_data = self.in_data_arr[idx-1].to_dict()
                if row["s_min"] == prev_data["e_min"] and row["s_sec"] == prev_data["e_sec"]:
                    #開始秒が前のデータの終了秒と同じ場合、前のデータの終了秒はnanを入れる
                    prev_row = rows[idx-1]
                    prev_row["e_min"] = np.nan
                    prev_row["e_sec"] = np.nan
                if row["s_min"] == prev_data["s_min"]:
                    #s_minが前のデータのs_minと同じ場合、s_minにはnanを入れる
                    row["s_min"] = np.nan

            #終了秒が0:0の場合、終了秒はnanを入れる
            if row["e_min"] == 0 and row["e_sec"] == 0:
                row["e_min"] =np.nan
                row["e_sec"] =np.nan

            rows.append(row)

        df = pandas.DataFrame(rows)
        df.to_excel(args.out_excel_file,index=False)
        print(f"出力しました：{args.out_excel_file}")

    def excel2file(self,args):
        """
        input形式excelを読み込んでファイルを出力する
        テンプレートメソッド
        """
        #excelファイル読み込み
        self.read_excel(args)

        #入力データチェック        
        self.check_data()

        #ファイル出力
        self.out_file() #子クラスで実装


def format_timedelta(td:timedelta)->str:
    """
    引数：
    td: timedelta
    戻り値：
    "MM:SS"
    """
    min = int(td.seconds /60)
    sec = int(td.seconds % 60)
    return f"{min:02}:{sec:02}"

class AppException(Exception):
    pass

def read_jsonc(f):
    """
    jsonc（コメント付きjson）ファイルを読み込む
    """
    text = f.read()
    re_text = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text)    # コメントを削除
    return json.loads(re_text)
