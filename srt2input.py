#!/usr/bin/env python3
import argparse
from lib.common import InputData,InputBase,print_args,AppException
import pyparsing as pp

"""
SRT形式ファイルからinput形式excelファイルに変換
"""

class Process(InputBase):
    def __init__(self):
        super().__init__()

    def read_srt(self):
        """
        SRT形式ファイルをInputDataのリストに読み込む
        """
        with open(args.in_file,encoding='utf-8') as f:
            data = f.read()

        #parser作成
        #no      = pp.LineStart()+pp.Word(pp.nums).set_results_name("no")+pp.LineEnd()
        no      = pp.Word(pp.nums).set_results_name("no")+pp.LineEnd()
        start   = pp.Word(pp.nums)("s_hour")+pp.Suppress(":")+pp.Word(pp.nums)("s_min")+pp.Suppress(":")+ \
            pp.Word(pp.nums)("s_sec")+pp.Suppress(",")+pp.Word(pp.nums).suppress()
        end     = pp.Word(pp.nums)("e_hour")+pp.Suppress(":")+pp.Word(pp.nums)("e_min")+pp.Suppress(":")+ \
            pp.Word(pp.nums)("e_sec")+pp.Suppress(",")+pp.Word(pp.nums).suppress()
        time_span = start + pp.Suppress("-->") + end
        subtitles  = pp.OneOrMore(pp.Word(pp.pyparsing_unicode.printables+" "),stop_on=no).set_results_name("subtitles")

        parser = no + time_span+ subtitles

        res = parser.search_string(data)

        if args.subtitle_langs is not None:
            subtitle_langs = args.subtitle_langs.split(",")
        
        num_langs = None    #言語の数
        #InputDataのリストに読み込む
        for idx,data in enumerate(res):
            no =  int(data["no"])
            s_hour  = int(data["s_hour"])
            s_min   = int(data["s_min"])
            s_sec   = int(data["s_sec"])
            e_hour  = int(data["e_hour"])
            e_min   = int(data["e_min"])
            e_sec   = int(data["e_sec"])
            subtitles  = data["subtitles"].as_list()

            #字幕の行数＝言語の数が一致しているかチェック
            if num_langs is None:
                num_langs = len(subtitles)
            else:
                if len(subtitles) != num_langs:
                    raise AppException(f"字幕の行数が以前とちがう：NO={no}")

            if args.subtitle_langs is not None and len(subtitles)<len(subtitle_langs):
                raise AppException(f"字幕の行数が指定された言語数より少ない：NO={no}")
            
            dic = {}
            if args.subtitle_langs is not None:
                for idx,lang in enumerate(subtitle_langs):
                    dic[lang] = subtitles[idx]
            else:
                for idx in range(0,num_langs):
                    lang = f"L{idx+1}"
                    dic[lang] = subtitles[idx]

            data = InputData(index=idx+1,
                             s_hour=s_hour,s_min=s_min,s_sec=s_sec,
                             e_hour=e_hour,e_min=e_min,e_sec=e_sec,
                             subtitles=dic)
            self.in_data_arr.append(data)

    def main(self):
        self.read_srt()
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'       ,help="入力SRTファイル")    
    parser.add_argument('out_excel_file',help="出力excelファイル")
    parser.add_argument('--subtitle_langs',
                        help="入力SRTファイルの言語のリスト。カンマ区切り。省略時はL1,L2…とする"
                        )
        
    args = parser.parse_args()
    print_args(args)

    proc = Process()
    try:
        proc.main()
    except AppException as e:
        print(e)