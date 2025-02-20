from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests as req
import xml.etree.ElementTree as ET
from lib.common import AppException,Settings
import pickle
import os

#Translate API
#APIのURL
#https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/mt/generalPT_pt_ja/
URL             = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp'
API_NAME        = "mt"
DICT_SAVE_PATH  = "data/dict_save.txt"  #翻訳中にエラーが起きた場合、途中まで訳したdictを保存

class Translate:
    def __init__(self):
        client = BackendApplicationClient(client_id=Settings.api['KEY'])
        oauth = OAuth2Session(client=client)
        token_url = URL + '/oauth2/token.php'
        try:
            self.token = oauth.fetch_token(
                token_url=token_url, client_id=Settings.api["KEY"], client_secret=Settings.api["SECRET"]
                )
        except Exception as e:
            raise AppException(f"api実行時エラー：{e.str}")        

    def translate(self,text,api_param):
        try:
            params = {
                'access_token'  : self.token['access_token'],  # アクセストークン
                'key'           : Settings.api["KEY"],        # API key
                'name'          : Settings.api["NAME"],       # ログインID
                'api_name'      : API_NAME,               # API名
                'api_param'     : api_param,              # API値
                'text'          : text
            }
            
            res = req.post(URL + '/api/?', data=params)
            res.encoding = 'utf-8'
            #print(res)         #httpレスポンス
            #print(res.text)    #xml
            root=ET.fromstring(res.text)
            elem = root.find("./result/text")
            return elem.text

        except Exception as e:
            raise AppException(f"api実行時エラー：{e.str}")
    
    def make_dict(self,org_lang,langs:list,set_org:set)->dict:
        """
        辞書を作成する。同じ原文は１回の翻訳で済ますため
        
        DICT_SAVE_PATHのファイルがあればそこから翻訳結果を読み込む
        翻訳中エラー時は途中までの翻訳結果をDICT_SAVE_PATHに保存
        引数：
            org_lang    原文の言語
            langs:      翻訳先言語のリスト。config/api.jsoncのキー。例：["eng","jp"]
            set_org:    重複を除いた原文のリスト
        戻り値：
            {原文:{翻訳先言語:翻訳結果,},}
        """
        print(f"{len(set_org)}件の原文を翻訳します")
        dic ={}
        
        if os.path.exists(DICT_SAVE_PATH):
            #前回の途中までの編訳結果ファイルがあれば読み込む
            print(f"前回の途中までの編訳結果を使用します：{DICT_SAVE_PATH}")
            with open(DICT_SAVE_PATH,encoding='utf-8') as f:
               dic = pickle.load(f)
            print(f"前回の途中までの編訳結果を{len(dic)}件読み込みました")

        cnt = 0 #翻訳した原文の数
        for idx,org in enumerate(set_org):
            print(f"\r{idx+1}件目の原文を処理",end="")
            if not org in dic.keys():
                dic[org]={}
            for lang in langs:
                if not lang in dic[org].keys():
                    try:
                        ret = self.translate(org,Settings.api["api"][org_lang][lang])
                    except Exception as e:
                        if cnt>0:
                            #途中までの翻訳結果を保存
                            with open(DICT_SAVE_PATH,"w",encoding="utf-8") as f:
                                pickle.dump(dic,f)
                                print(f"エラーのため翻訳を中断。{cnt}件の原文を翻訳しました") 
                                print(f"途中までの編訳結果を保存しました：{DICT_SAVE_PATH}")
                        raise e
                    dic[org][lang]=ret
                    if len(dic[org]) == len(langs):
                        cnt +=1
        print("")
        return dic
