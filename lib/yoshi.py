"""
自作ライブラリからコピーした関数
"""

import pandas
from openpyxl.utils import get_column_letter
import unicodedata
import re
import json

def read_jsonc(f):
    """
    jsonc（コメント付きjson）ファイルを読み込む
    """
    text = f.read()
    # コメントを削除
    # (?<!:)//.*'
    # urlのhttp://にマッチさせない
    re_text = re.sub(r'/\*[\s\S]*?\*/|(?<!:)//.*', '', text)    
    return json.loads(re_text)

def count_zen_han(s: str) -> int:
    """
    文字列の長さを求める。全角は2、半角は1でカウントする
    
    :param s: 文字列
    :type s: str
    :return: 文字列の長さ
    :rtype: int
    """
    length = 0
    for ch in s:
        # East Asian Width が 'F' (全角), 'W' (全角), 'A' (曖昧) の場合は2
        if unicodedata.east_asian_width(ch) in ('F', 'W','A'):
            length += 2
        else:
            length += 1
    return length

def df2excel(df,excel_path):
    """
    pandas.dataframeをexcelファイルに出力する
    列幅をデータの長さに合わせる
    
    :param df: pandas.dataframe
    :param excel_path: 出力するexcelファイルのパス
    """
    col_width_margin = 4  #列幅に加算する余裕
    with pandas.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        ws = writer.sheets["Sheet1"]

        # 列幅をデータの長さに合わせる
        for col_idx, col in enumerate(df.columns, 1):
            max_length = max(
                df[col].astype(str).map(count_zen_han).max(),
                count_zen_han(col)
            )
            ws.column_dimensions[get_column_letter(col_idx)].width = max_length + col_width_margin
