import argparse
from lib.translate import Translate
from lib.common import InputData,InputBase,Settings
import pyparsing as pp

"""
文字起こしファイルからexcelのinput形式ファイルを作成
翻訳を追加
"""
class Process(InputBase):
    def __init__(self):
        super().__init__()

    def read_transcription(self):
        """
        文字起こしファイルをInputDataの配列に読み込む
        """
        with open(args.in_file,encoding='utf-8') as f:
            data = f.read()

        #parser作成
        #startは通番。原文の中の数字にマッチしないように、LineStart/LineEndで囲む
        start   = pp.LineStart()+pp.Word(pp.nums)("s_min")+pp.Suppress(":")+ pp.Word(pp.nums)("s_sec")+pp.LineEnd()
        lyric   = pp.Word(pp.pyparsing_unicode.printables+" ").set_results_name("org")

        parser = start + lyric

        res = parser.search_string(data)

        #InputDataのリストに読み込む
        for idx,data in enumerate(res):
            s_min   = int(data["s_min"])
            s_sec   = int(data["s_sec"])
            subtitles = {Settings.api["org_lang"]:data["org"]}
            for lang in Settings.api["translate_langs"]:
                subtitles[lang]=""
            data = InputData(index=idx+1,
                             s_hour=0,s_min=s_min,s_sec=s_sec,
                             #終了秒には0:0:0を入れておく。excel出力時はnanに変換する（InputBase.out_excel）
                             e_hour=0,e_min=0,e_sec=0,   
                             subtitles=subtitles)
            self.in_data_arr.append(data)

    def translate(self):
        """
        InputDataに翻訳を追加する
        """
        set_org = set([data.subtitles[Settings.api["org_lang"]] for data in self.in_data_arr]) #重複を除いた原文のリスト

        tl = Translate()
        dic = tl.make_dict(Settings.api["org_lang"],Settings.api["translate_langs"],set_org)
        #訳を追加
        for data in self.in_data_arr:
            org = data.subtitles[Settings.api["org_lang"]]
            for lang in Settings.api["translate_langs"]:
                data.subtitles[lang]    = dic[org][lang]
   
    def main(self):
        self.read_transcription()
        self.translate()
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="文字起こしファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル。input形式')
    args = parser.parse_args()
    print(f"引数：{args}")

    proc=Process()
    proc.main()
