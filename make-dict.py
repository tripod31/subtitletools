import argparse
import re
from lib.translate import Translate
from lib.common import AppException,Settings

def make_dict():

    dic_in ={}    #翻訳対象の辞書
    with open(args.in_file,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if (len(line)==0):
                continue
            arr = re.split(r"[ ,\(\)]",line.strip())
            words = [word.lower() for word in arr if len(word)>0]
            for word in words:
                dic_in[word]=["jp"]

    tl = Translate(args.test)
    org_lang = Settings.api["org_lang"]
    dic=tl.make_dict(org_lang,dic_in)

    words = list(dic.keys())
    words.sort()

    with open(args.out_file,"w",encoding='utf-8') as f:
        for word in words:
            f.write(f"{word},{dic[word]["jp"]}\n")

    print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'   ,help="入力する原文ファイル")
    parser.add_argument('out_file'  ,help="出力するCSV。辞書ファイル")
    parser.add_argument('--test',
                        action="store_true",
                        help='テスト用。APIでの翻訳を行わない')       
    args = parser.parse_args()
    print(f"引数：{args}")

    try:
        make_dict()
    except AppException as e:
        print(e)
        