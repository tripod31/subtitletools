import argparse
from lib.translate import Translate
from lib.common import InputData,InputBase,Settings

"""
原文からexcelのinput形式ファイルを作成
翻訳を追加
"""
class Process(InputBase):
    def __init__(self):
        super().__init__()

    def read_transcription(self):
        """
        文字起こしファイルをInputDataの配列に読み込む
        """
        lines=[]
        with open(args.in_file,encoding='utf-8') as f:
            line = f.readline().strip()
            if len(line)>0:
                lines.append(line)

        #InputDataのリストに読み込む
        for idx,line in enumerate(lines):
            subtitles = {Settings.api()["org_lang"]:line}
            for lang in Settings.api()["translate_langs"]:
                subtitles[lang]=""
            data = InputData(index=idx+1,
                             #　終了/開始秒には0:0:0を入れておく。excel出力時はnanに変換する
                             # （InputBase.out_excel）                             
                             s_hour=0,s_min=0,s_sec=0,
                             e_hour=0,e_min=0,e_sec=0,   
                             subtitles=subtitles)
            self.in_data_arr.append(data)

    def translate(self):
        """
        InputDataに翻訳を追加する
        """
        set_org = set([data.subtitles[Settings.api()["org_lang"]] for data in self.in_data_arr]) #重複を除いた原文のリスト

        tl = Translate()
        dic = tl.make_dict(Settings.api()["org_lang"],Settings.api()["translate_langs"],set_org)
        #訳を追加
        for data in self.in_data_arr:
            org = data.subtitles[Settings.api()["org_lang"]]
            for lang in Settings.api()["translate_langs"]:
                data.subtitles[lang]    = dic[org][lang]
   
    def main(self):
        self.read_transcription()
        self.translate()
        self.out_excel(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'           ,help="原文ファイル")
    parser.add_argument('out_excel_file'    ,help='出力excelファイル。input形式')
    args = parser.parse_args()
    print(f"引数：{args}")

    proc=Process()
    proc.main()
