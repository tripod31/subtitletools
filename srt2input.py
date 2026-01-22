#!/usr/bin/env python3
import argparse
from lib.common import InputData,InputBase,Settings,print_args
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

        subtitle_langs = args.subtitle_langs.split(",")
        #InputDataのリストに読み込む
        for idx,data in enumerate(res):
            s_hour  = int(data["s_hour"])
            s_min   = int(data["s_min"])
            s_sec   = int(data["s_sec"])
            e_hour  = int(data["e_hour"])
            e_min   = int(data["e_min"])
            e_sec   = int(data["e_sec"])
            subtitles  = data["subtitles"].as_list()
            dic = {}
            for idx,lang in enumerate(subtitle_langs):
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
    parser.add_argument('subtitle_langs',
                        help="入力SRTファイルの言語のリスト。カンマ区切り")
        
    args = parser.parse_args()
    print_args(args)

    proc = Process()
    proc.main()
