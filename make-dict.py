import argparse
import re
from lib.translate import Translate

API_PARAM_JP="generalPT_pt_ja"

def make_dict():
    tl = Translate()

    words =set()    #単語のリスト
    with open(args.in_file,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if (len(line)==0):
                continue
            arr = re.split(r"[ ,\(\)]",line.strip())
            arr = [word.lower() for word in arr]
            words = words | set(arr)

    words=list(words)
    words.remove("")
    words.sort()

    with open(args.out_file,"w",encoding='utf-8') as f:
        for i in range(0,len(words)):
            print(f"\r{i+1}/{len(words)}件処理",end="")
            word = words[i]
            word_jp = tl.translate(word,API_PARAM_JP)
            f.write(f"{word},{word_jp}\n")

    print(f"\n{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'   ,help="入力する原文ファイル")
    parser.add_argument('out_file'  ,help="出力するCSV。辞書ファイル")
    args = parser.parse_args()
    print(f"引数：{args}")

    make_dict()