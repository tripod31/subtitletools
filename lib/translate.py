from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import requests as req
import xml.etree.ElementTree as ET
from lib.common import AppException,Settings

class Translate:
    URL = 'https://mt-auto-minhon-mlt.ucri.jgn-x.jp'   #APIのURL 

    def __init__(self):
        
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
        try:
            params = {
                'access_token'  : self.token['access_token'],  # アクセストークン
                'key'           : Settings.api["KEY"],        # API key
                'name'          : Settings.api["NAME"],       # ログインID
                'api_name'      : "mt",                       # API名
                'api_param'     : api_param,                  # API値
                'text'          : text
            }
            print(f"翻訳API実行：{len(text.split("\n"))}行 org_lang={org_lang} to_lang={to_lang}")
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

