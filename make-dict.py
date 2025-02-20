import argparse
import re
from lib.translate import Translate

def make_dict():

    words =set()    #単語のリスト
    with open(args.in_file,encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if (len(line)==0):
                continue
            arr = re.split(r"[ ,\(\)]",line.strip())
            arr = [word.lower() for word in arr if len(word)>0]
            words = words | set(arr)

    tl = Translate()
    org_lang = "pt"
    dic = tl.make_dict(org_lang,["jp"],words)
    words = list(words)
    words.sort()

    with open(args.out_file,"w",encoding='utf-8') as f:
        for word in words:
            f.write(f"{word},{dic[word]["jp"]}\n")

    print(f"{args.out_file}：出力しました")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'   ,help="入力する原文ファイル")
    parser.add_argument('out_file'  ,help="出力するCSV。辞書ファイル")
    args = parser.parse_args()
    print(f"引数：{args}")

    make_dict()