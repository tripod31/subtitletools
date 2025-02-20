#!/usr/bin/env python3
# coding:utf-8
import unittest
import subprocess
from lib.common import read_jsonc

class Test1(unittest.TestCase):

    def setUp(self):
        with open('.vscode\\launch.json', 'r',encoding='utf-8') as f:
            self.json = read_jsonc(f)
    
    def exec(self,config):
        """
        引数
        config
            launch.jsonの中の一つの実行設定のdict
        """
        print(config["name"]+"\t:",end="")
        program = config["program"]
        args = config["args"]                
        arr = ["python.exe",program]
        arr.extend(args)
        cmd = " ".join(arr)
        #print(f"exec command:{cmd}")
        res = subprocess.run(cmd,capture_output=True,shell=True,text=True,encoding="utf-8")
        if res.stderr is not None and len(res.stderr)>0:
            print(res.stderr)
        else:
            print("OK")

        return res.returncode

    def test_launch(self):
        """
        各スクリプトを実行し、正常終了することを確認
        launch.jsonの中の実行設定を実行し、戻り値が0であることをチェック
        """
        conf_names = ["input2srt","input2txt","srt2input","addsec2input"]
        configs = {conf["name"]:conf for conf in self.json["configurations"]}
        err_cnt=0
        for conf_name in conf_names:
            config = configs[conf_name]
            ret = self.exec(config)
            if ret != 0:
                err_cnt += 1
        self.assertEqual(err_cnt, 0)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
