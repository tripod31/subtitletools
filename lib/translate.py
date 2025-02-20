from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests as req
import xml.etree.ElementTree as ET
from lib.common import AppException,read_jsonc,Settings

#Translate API
#APIのURL
#https://mt-auto-minhon-mlt.ucri.jgn-x.jp/api/mt/generalPT_pt_ja/
URL             = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp'
API_NAME        = "mt"

class Translate:
    def __init__(self):
        client = BackendApplicationClient(client_id=Settings.api()['KEY'])
        oauth = OAuth2Session(client=client)
        token_url = URL + '/oauth2/token.php'
        try:
            self.token = oauth.fetch_token(
                token_url=token_url, client_id=Settings.api()["KEY"], client_secret=Settings.api()["SECRET"]
                )
        except Exception as e:
            print('=== Error ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))
            raise AppException("api実行時エラー")        

    def translate(self,text,api_param):
        try:
            params = {
                'access_token'  : self.token['access_token'],  # アクセストークン
                'key'           : Settings.api()["KEY"],        # API key
                'name'          : Settings.api()["NAME"],       # ログインID
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
            print('=== Error ===')
            print('type:' + str(type(e)))
            print('args:' + str(e.args))
            print('e:' + str(e))
            raise AppException("api実行時エラー")
    
    def make_dict(self,org_lang,langs:list,set_org:set)->dict:
        """
        辞書を作成する。同じ原文は１回の翻訳で済ますため
        引数：
            org_lang    原文の言語
            langs:      翻訳先言語のリスト。config/api.jsoncのキー。例：["eng","jp"]
            set_org:    重複を除いた原文のリスト
        戻り値：
            {原文:{翻訳先言語:翻訳結果,},}
        """
        print(f"{len(set_org)}件翻訳します")
        dic ={}
        for idx,org in enumerate(set_org):
            print(f"\r{idx+1}件目処理",end="")
            dic[org]={}
            for lang in langs:
                ret = self.translate(org,Settings.api()["api"][org_lang][lang])
                dic[org][lang]=ret
        print("")
        return dic
