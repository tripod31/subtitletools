from datetime import timedelta
import pandas
import math
import numpy as np
from lib.yoshi import df2excel,read_jsonc

#input.xlsxの開始/終了秒の列名
TIME_COLUMNS=["s_hour","s_min","s_sec","e_hour","e_min","e_sec"]

def format_timedelta(td:timedelta)->str:
    """
    引数：
    td: timedelta
    戻り値：
    "MM:SS"
    """
    hour = int(td.seconds /(60*60))
    min = int((td.seconds % (60*60))/60)
    sec = int(td.seconds % 60)
    return f"{hour:02}:{min:02}:{sec:02}"

def print_args(args):
    """
    プログラムの引数を表示
    """
    arr = [f"{k} = {v}" for k,v in vars(args).items()]    
    print(f"引数：\n{"\n".join(arr)}")

class AppException(Exception):
    pass

class Settings:
    api = {}  #config/api.jsoncを読み込む

    @classmethod
    def init(cls):
        with open("config/api.jsonc",encoding='utf-8') as f:
            cls.api = read_jsonc(f)

class InputData:
    """
    input形式ファイル(input.xlsx)の一行に対応する
    """
    def __init__(self,index:int,s_hour:int,s_min:int,s_sec:int,e_hour:int,e_min:int,e_sec:int,subtitles:dict):
        """
        引数：
            subtitles:  dict:{言語:字幕の一行}
        """
        self.index       = index
        self.start       = timedelta(hours=s_hour,minutes=s_min,seconds=s_sec)
        self.end         = timedelta(hours=e_hour,minutes=e_min,seconds=e_sec)
        self.subtitles = subtitles

    def to_srt(self,langs:list|None=None)->list:
        """
        引数：
            langs:  出力する言語のリスト
        戻り値：
            SRT形式の文字列の配列
        """
        ret =[]
        ret.append(f"{self.index}") #通し番号
        line_time = f"{format_timedelta(self.start)},000 --> {format_timedelta(self.end)},000"
        ret.append(line_time)
        if langs is not None:
            for lang in langs:
                if not lang in self.subtitles.keys():
                    raise AppException(f"入力データに{lang}がありません")
                ret.append(self.subtitles[lang])
        else:
            #出力する言語のリストが指定されない場合、全て出力
            ret.extend(self.subtitles.values())
        return ret
    
    def to_dict(self)->dict:
        """
        戻り値：
            excel出力用のdict
            indexは出力しない
        """
        dic = {}
        dic["s_hour"]  = int(self.start.seconds/(60*60))
        dic["s_min"]   = int((self.start.seconds%(60*60))/60)
        dic["s_sec"]   = int(self.start.seconds % 60)
        dic["e_hour"]  = int(self.end.seconds/(60*60))
        dic["e_min"]   = int((self.end.seconds % (60*60))/60)
        dic["e_sec"]   = int(self.end.seconds % 60)
        for lang in self.subtitles:
            dic[lang]  = self.subtitles[lang]
        return dic

class InputBase():
    """
    InputDataを操作する
    """

    def __init__(self):
        self.in_data_arr=[] #InputDataのリスト
        self.excel_langs=[] #excelファイルの列名から言語のリストを得る
        self.subtitle_langs=None  #出力する字幕の言語リスト

    def read_excel(self,args):
        """
        excelファイルから読み込む
        ルール：
        １行目にstartが無ければエラー
        s_hour/s_minが無ければ前の行のs_hour/s_minをs_hour/s_minとする
        endが無ければ一つ後の行の開始秒をendとする
        e_hour/e_minが無ければs_hour/s_minをe_hour/e_minとする
        最終行にendが無ければエラー
        """
        #excelファイル読み込み
        df = pandas.read_excel(args.in_excel_file,header=0)
        self.excel_langs=list(df.columns)[6:]
        
        # 開始秒が空のデータを埋める
        for idx,row in df.iterrows():
            # 注意：dfの値を書き換える時、df.iterrows()のrow["列名"]=値では書き換えられない。df.at()で書き換える
            if idx == 0:
                #最初の行                
                if math.isnan(row["s_hour"]):            
                    df.at[idx,"s_hour"] = 0
                if math.isnan(row["s_min"]):
                    raise AppException("１行目にs_minがありません")
                if math.isnan(row["s_sec"]):
                    raise AppException("１行目にs_secがありません")
            else:
                prev_row = df.loc[idx -1]
                if math.isnan(row["s_hour"]):
                    df.at[idx,"s_hour"] = prev_row["s_hour"]
                if math.isnan(row["s_min"]):
                    df.at[idx,"s_min"] = prev_row["s_min"]
                if math.isnan(row["s_sec"]):
                    raise AppException(f"{idx+1}行目にs_secがありません")                

        #終了秒が空のデータを埋める
        for idx,row in df.iterrows():
            if math.isnan(row["e_hour"]) and math.isnan(row["e_min"]) and math.isnan(row["e_sec"]):
                #終了秒が空の場合
                if idx >= df.shape[0]-1:
                    #最終行の場合
                    raise AppException(f"{idx+1}行目：最終行にendがありません")
                else:
                    #次の行の開始秒を終了秒とする
                    next_row = df.loc[idx +1]
                    df.at[idx,"e_hour"]   = next_row["s_hour"]
                    df.at[idx,"e_min"]    = next_row["s_min"]
                    df.at[idx,"e_sec"]    = next_row["s_sec"]
            else:
                #e_hour/e_minが空の場合、s_hour/s_minを値とする
                if math.isnan(row["e_hour"]):
                    df.at[idx,"e_hour"] = row["s_hour"]
                if math.isnan(row["e_min"]):
                    df.at[idx,"e_min"] = row["s_min"]

        #空のデータを埋めたdataframeから読み込む
        for idx,row in df.iterrows():
            self.read_row(idx,row)

    def read_row(self,index:int,row):
        """
        Excelから読み込んだDaraFrame一行分をInputDataオブジェクトに読み込む
        """
        s_hour  = row["s_hour"]
        s_min   = row["s_min"]
        s_sec   = row["s_sec"]
        e_hour  = row["e_hour"]
        e_min   = row["e_min"]
        e_sec   = row["e_sec"]
        subtitles = {}
        for idx in range(6 ,len(row)):
            lang = row.index[idx]    #言語=列名
            #字幕文が空の場合、長さ0の文字列をセット
            subtitles[lang] = row.iloc[idx] if not pandas.isnull(row.iloc[idx]) else ""  

        data = InputData(index+1,
                         s_hour=int(s_hour),s_min=int(s_min),s_sec=int(s_sec),
                         e_hour=int(e_hour),e_min=int(e_min),e_sec=int(e_sec),
                         subtitles=subtitles)
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
        shour/s_minが前のデータのs_hour/s_minと同じ場合、s_hour/s_minにはnanを入れる
        開始/終了秒が0:0:0の場合、開始/終了秒はnanを入れる
        """
        rows_org = [data.to_dict() for data in self.in_data_arr]    #書き換える前のデータリスト

        rows = []   #出力用データリスト
        for idx,data in enumerate(self.in_data_arr):
            row_org = rows_org[idx]
            row = data.to_dict()    #出力用データ
            if idx < len(self.in_data_arr)-1:
                #終了時/分が開始時/分と同じ場合、終了時/分にはnanを入れる
                if row_org["e_hour"] == row_org["s_hour"]:
                    row["e_hour"] = np.nan
                if row_org["e_min"] == row_org["s_min"]:
                    row["e_min"] = np.nan            
            if idx >0:
                prev_row_org = rows_org[idx-1]
                if row_org["s_hour"] == prev_row_org["e_hour"] and \
                    row_org["s_min"] == prev_row_org["e_min"] and \
                    row_org["s_sec"] == prev_row_org["e_sec"]:
                    #開始秒が前のデータの終了秒と同じ場合、前のデータの終了秒はnanを入れる
                    prev_row = rows[idx-1]
                    prev_row["e_hour"] = np.nan
                    prev_row["e_min"] = np.nan
                    prev_row["e_sec"] = np.nan
                if row_org["s_hour"] == prev_row_org["s_hour"]:
                    #s_hourが前のデータのs_hourと同じ場合、s_hourにはnanを入れる
                    row["s_hour"] = np.nan
                if row_org["s_min"] == prev_row_org["s_min"]:
                    #s_minが前のデータのs_minと同じ場合、s_minにはnanを入れる
                    row["s_min"] = np.nan

            #終了時/分が開始時/分と同じ場合、終了時/分にはnanを入れる
            if row_org["e_hour"] == row_org["s_hour"]:
                row["e_hour"] = np.nan
            if row_org["e_min"] == row_org["s_min"]:
                row["e_min"] = np.nan 

            #開始秒が0:0:0の場合、開始秒はnanを入れる
            if idx>0 and row_org["s_hour"] == 0 and row_org["s_min"] == 0 and row_org["s_sec"] == 0:
                row["s_hour"] =np.nan
                row["s_min"] =np.nan
                row["s_sec"] =np.nan

            #終了秒が0:0:0の場合、終了秒はnanを入れる
            if row_org["e_hour"] == 0 and row_org["e_min"] == 0 and row_org["e_sec"] == 0:
                row["e_hour"] =np.nan
                row["e_min"] =np.nan
                row["e_sec"] =np.nan

            rows.append(row)

        df = pandas.DataFrame(rows)
        df2excel(df,args.out_excel_file)
        print(f"出力しました：{args.out_excel_file}")

    def excel2file(self,args):
        """
        input形式excelを読み込んでファイルを出力する
        テンプレートメソッド
        """
        if args.subtitle_langs is not None:
            self.subtitle_langs = args.subtitle_langs.split(",")

        #excelファイル読み込み
        self.read_excel(args)

        #excelから読み込んだ言語と引数で指定された出力言語を比較
        if self.subtitle_langs is not None:
            langs_missing = [ lang for lang in self.subtitle_langs if not lang in self.excel_langs]
            if len(langs_missing)>0:
                #excelファイルの言語以外が出力言語に指定されている場合はエラー
                raise AppException(f"excelファイルの言語以外が出力言語に指定されている：{','.join(langs_missing)}")

        #入力データチェック        
        self.check_data()

        #ファイル出力
        self.out_file() #子クラスで実装

#モジュール初期化
Settings.init()