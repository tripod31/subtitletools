from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests as req
import xml.etree.ElementTree as ET
from lib.common import AppException,Settings
import json
import os

#Translate API
DICT_SAVE_PATH  = "data/dict_save.json"  #翻訳中にエラーが起きた場合、途中まで訳したdictを保存

class Translate:
    URL = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp'   #APIのURL 

    def __init__(self,test=False):
        """
        引数：
        test:   True/False:True時はAPIによる翻訳を行わない
        """
        self.test = test
        if self.test:
            return
        
        client = BackendApplicationClient(client_id=Settings.api['KEY'])
        oauth = OAuth2Session(client=client)
        token_url = Translate.URL + '/oauth2/token.php'
        try:
            self.token = oauth.fetch_token(
                token_url=token_url, client_id=Settings.api["KEY"], client_secret=Settings.api["SECRET"]
                )
        except Exception as e:
            raise AppException(f"api実行時エラー：{e}")        

    def translate(self,text,org_lang,to_lang):
        """
        引数：
            text:   翻訳する原文
            org_lang:   原文の言語
            to_lang:    翻訳先の言語   
        """
        api_param = Settings.api["api"][org_lang][to_lang]
        if self.test:
            #テスト時はAPIによる翻訳を行わない
            if text == "TEST-ERROR":
                #翻訳時エラーのテスト用
                raise AppException("テスト翻訳エラー")
            return f"{api_param}[{text}]"
        
        try:
            params = {
                'access_token'  : self.token['access_token'],  # アクセストークン
                'key'           : Settings.api["KEY"],        # API key
                'name'          : Settings.api["NAME"],       # ログインID
                'api_name'      : "mt",                       # API名
                'api_param'     : api_param,                  # API値
                'text'          : text
            }
            
            res = req.post(Translate.URL + '/api/?', data=params)
            res.encoding = 'utf-8'
            #print(res)         #httpレスポンス
            #print(res.text)    #xml
            root=ET.fromstring(res.text)
            elem = root.find("./code")
            code = elem.text
            if code != "0":
                elem = root.find("./message")
                msg = elem.text
                raise AppException(f"api実行時エラー：code：{code}　message：{msg}")
            elem = root.find("./result/text")
            return elem.text

        except Exception as e:
            raise AppException(f"api実行時エラー：{e}")

    def count_dict(self,dic):
        """
        dicの要素数を返す
        """
        #dic[k]はmake_dictの引数の場合はlist。make_dictの戻り値の場合はlist。どちらもlenで要素数が取れる
        count = sum([len(dic[k]) for k in dic.keys()])         
        return count

    def read_dict(self)->dict:
        """
        前回の途中までの編訳結果ファイルがあれば読み込む
        """
                    
        dic ={}
        if os.path.exists(DICT_SAVE_PATH):
            print(f"前回の途中までの編訳結果を読み込みます：{DICT_SAVE_PATH}")
            try:
                with open(DICT_SAVE_PATH,"r") as f:
                    dic = json.load(f)
                count = self.count_dict(dic)            
                print(f"前回の途中までの編訳結果を{count}件読み込みました")
            except Exception as e:
                print(f"{DICT_SAVE_PATH}の読み込みに失敗しました：{e}")

        return dic

    def write_dict(self,dic:dict):
        """
        途中までの翻訳結果を保存
        """
        count = self.count_dict(dic)
        try:
            with open(DICT_SAVE_PATH,"w") as f:
                json.dump(dic,f,indent=4)
            print(f"途中までの編訳結果{count}件を保存しました：{DICT_SAVE_PATH}")
        except Exception as e:
            print(f"{DICT_SAVE_PATH}の書き込みに失敗しました：{e}")

    def make_dict(self,org_lang,dic_in)->dict:
        """
        辞書を作成する。同じ原文は１回の翻訳で済ますため
        
        DICT_SAVE_PATHのファイルがあればそこから翻訳結果を読み込む
        翻訳中エラー時は途中までの翻訳結果をDICT_SAVE_PATHに保存
        引数：
        org_lang:    原文の言語
        dic_in:
            {原文:[翻訳先言語,],}
        戻り値：
            {原文:{翻訳先言語:翻訳結果,},}
        """
        total_count = self.count_dict(dic_in)
        print(f"{total_count}件翻訳します")
        dic_prev =self.read_dict()   #前回エラー時に保存した途中までの翻訳を読み込む

        cnt = 0 #翻訳した件数
        dic_ret={}
        for org in dic_in.keys():  #org:原文
            for to_lang in dic_in[org]:    #lang:翻訳先言語
                if org in dic_prev.keys() and to_lang in dic_prev[org].keys():
                    #前回エラー時に翻訳済の場合、その訳を利用する
                    print(f"翻訳済：{org}:{to_lang}")
                    if not org in dic_ret:
                        dic_ret[org]={}
                    dic_ret[org][to_lang] =  dic_prev[org][to_lang]
                    continue
                try:
                    ret = self.translate(org,org_lang,to_lang)
                except Exception as e:
                    print(f"エラーのため翻訳を中断") 
                    if cnt>0:
                        self.write_dict(dic_ret)
                    raise e

                if not org in dic_ret:
                    dic_ret[org]={}                
                dic_ret[org][to_lang]=ret
                cnt +=1
                print(f"\r{cnt}件翻訳済。",end="")
        print("")
        
        if not self.test and os.path.exists(DICT_SAVE_PATH):
            os.remove(DICT_SAVE_PATH)

        return dic_ret