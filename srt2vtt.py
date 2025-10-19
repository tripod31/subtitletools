import argparse
from lib.common import print_args

"""
SRT形式ファイル→VTT形式ファイル変換
・最初の行にWEBVTTを付加
・1秒以下の指定は.で始まる
"""
class AppException(Exception):
    pass

class Process:
    def main(self):
        self.out_file(args.in_file,args.out_file)
        print(f"出力しました：{args.out_file}")

    def out_file(self,in_path,out_path):
        with open(in_path,"r",encoding='utf-8') as f:
            lines=f.readlines()
        with open(out_path,"w",encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for line in lines:
                f.write(line.replace(",000",".000"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_file'       ,help="入力SRT形式ファイル") 
    parser.add_argument('out_file'      ,help="出力VTT形式ファイル") 
    
    args = parser.parse_args()
    print_args(args)
    proc=Process()
    try:
        proc.main()
    except AppException as e:
        print(e)