#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox,ttk
import json
import os
import subprocess
from lib.common import read_jsonc,AppException

TITLE="スクリプト実行"
LAUNCH_SAVE_JSON= "config/launch_save.json" #選択を保存するファイル
LAUNCH_SAVE_JSON= "config/launch_save.json" #選択を保存するファイル
LAUNCH_SETTINGS_JSON= "config/launch_settings.jsonc" 

DATA_DIR="data"

class Process:
    def __init__(self):
        if os.path.exists(LAUNCH_SETTINGS_JSON):
            with open(LAUNCH_SETTINGS_JSON) as f:
                self.settings=read_jsonc(f)
        else:
            raise AppException(f"{LAUNCH_SETTINGS_JSON}がありません")

        if os.path.exists(LAUNCH_SAVE_JSON):
            #選択状態をjsonファイルから読み込む
            with open(LAUNCH_SAVE_JSON) as f:
                saved_info=json.load(f)  
        else:
            #jsonファイルがない場合の初期値
            saved_info={
                # script_type:
                #   "file2input":ファイルからinput*.xlsx出力
                #   "input2file":input*.xlsからファイル出力                
                "script_type":  "file2input",
                "script_idx":   0,
                "geometry":     "466x366+1110+450"
            }
        self.saved_info = saved_info

    def on_close(self):
        #ウィンドウクローズ時

        #選択状態をjsonファイルに保存
        script_type = self.radio_var.get()
        if len(self.listbox_script.curselection())==0:
            messagebox(TITLE,"スクリプトを選択してください")
            return            
        script_idx = self.listbox_script.curselection()[0]

        settings = {
                "script_type":  script_type,
                "script_idx":   script_idx,
                "geometry":     self.root.geometry()     
        }
        with open(LAUNCH_SAVE_JSON,"w") as f:
            json.dump(settings,f,indent=4)

        self.root.destroy()

    def on_radio(self):
        #スクリプト種別選択時
        script_type = self.radio_var.get()
        scripts = self.settings["SCRIPTS"][script_type]
        self.list_var.set(scripts)
        self.listbox_script.select_clear(first=0,last=tk.END)
        self.listbox_script.select_set(first=0,last=0)
        self.disp_inout_file()

    def on_list(self,event):
        #スクリプト選択時
        self.disp_inout_file()

    def disp_inout_file(self):
        """
        スクリプトに対応する入出力ファイルのパスと、ファイルの状態を表示
        """
        script_type = self.radio_var.get()
        if len(self.listbox_script.curselection())==0:
            return
        script_idx = self.listbox_script.curselection()[0]
        script  = self.settings["SCRIPTS"][script_type][script_idx]
        infile  = self.settings["IN_OUTS"][script]["infile"]
        outfile = self.settings["IN_OUTS"][script]["outfile"]
        self.tv_info.item(0, values=("入力",infile,self.get_file_state(infile)))
        self.tv_info.item(1, values=("出力",outfile,self.get_file_state(outfile)))

    def is_file_exists(self,file):
        path = os.path.join(DATA_DIR,file)
        ret = False
        if os.path.exists(path):
            ret=True
        else:
            ret =False
        return ret

    def get_file_state(self,file):
        if self.is_file_exists(file):
            ret ="存在します"
        else:
            ret ="存在しません"
        return ret

    def on_exec(self):
        """
        スクリプト実行
        """
        script_type = self.radio_var.get()
        if len(self.listbox_script.curselection())==0:
            messagebox.showinfo(TITLE,"スクリプトを選択してください")
            return
        script_idx = self.listbox_script.curselection()[0]
        script = self.settings["SCRIPTS"][script_type][script_idx]
        infile  = self.settings["IN_OUTS"][script]["infile"]
        if not self.is_file_exists(infile):
            messagebox.showinfo(TITLE,f"{infile}が存在しません")
            return
        outfile = self.settings["IN_OUTS"][script]["outfile"]
        if self.is_file_exists(outfile):
            ret=messagebox.askokcancel(TITLE,f"{outfile}は上書きされます")
            if ret == False:
                return
        args =["python",script,os.path.join(DATA_DIR,infile),os.path.join(DATA_DIR,outfile)]
        ret = subprocess.run(args,shell=True)   #shell=Trueにしないと、ライブラリが読み込まれない？

    def main(self):
        root = tk.Tk()
        root.title(TITLE)
        root.geometry(self.saved_info["geometry"])
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        #スクリプト種別選択ラジオボックス
        frame1 = tk.Frame(root,relief= tk.SOLID,bd=1,padx=10,pady=10)
        radio_var = tk.StringVar(value=self.saved_info["script_type"])
        label1 = tk.Label(frame1, text="処理種別",width=15,anchor="w")
        radiobutton1 = tk.Radiobutton(frame1, text="ファイルからinput-*.xlsx出力",
                                      variable=radio_var, value="file2input",command=self.on_radio)
        radiobutton2 = tk.Radiobutton(frame1, text="input.xlsからファイル出力",
                                      variable=radio_var, value="input2file",command=self.on_radio)
        label1.grid(row=0,column=0,rowspan=2)
        radiobutton1.grid(row=0,column=1,sticky=tk.W)
        radiobutton2.grid(row=1,column=1,sticky=tk.W)
        frame1.pack(fill=tk.X)  

        #スクリプト選択リストボックス
        frame2 = tk.Frame(root,relief= tk.SOLID,bd=1,padx=10,pady=10)
        label2 = tk.Label(frame2, text="スクリプト",width=15,anchor="w")
        scripts = self.settings["SCRIPTS"][self.saved_info["script_type"]]
        list_var = tk.StringVar(value=scripts)
        listbox_script = tk.Listbox(frame2,height=3,listvariable=list_var,selectmode="single")
        listbox_script.select_set(first=self.saved_info["script_idx"])
        listbox_script.bind("<<ListboxSelect>>",self.on_list)
        label2.grid(row=0,column=0)
        listbox_script.grid(row=0,column=1)
        frame2.pack(fill=tk.X)

        #入力ファイル表示
        frame3 = tk.Frame(root,relief= tk.SOLID,bd=1,padx=10,pady=10)
        label3 = tk.Label(frame3, text="入出力ファイル",width=15,anchor="w")
        tv_info = ttk.Treeview(frame3,columns=(1,2,3),show="headings",height=2)

        tv_info.column(0,width=0)
        tv_info.column(1,width=60)
        tv_info.column(2,width=150)
        tv_info.column(3,width=100)

        tv_info.heading(0,text="dummy",anchor="w")
        tv_info.heading(1,text="入出力",anchor="w")
        tv_info.heading(2,text="ファイル",anchor="w")
        tv_info.heading(3,text="状態",anchor="w")
        
        tv_info.insert(parent='', index='end', iid=0 ,values=("入力","",""))
        tv_info.insert(parent='', index='end', iid=1 ,values=("出力","",""))

        label3.grid(row=0,column=0)
        tv_info.grid(row=0,column=1)
        frame3.pack(fill=tk.X)

        #実行ボタン
        frame4 = tk.Frame(root,relief= tk.SOLID,bd=1,padx=10,pady=10)
        button1 = tk.Button(frame4, text="実行",command=self.on_exec)
        button1.place(anchor=tk.CENTER,relx=0.5,rely=0.5,width=100)   #親フレームのcenterに置く
        frame4.pack(fill=tk.BOTH,expand=True)

        #他のメソッドから参照したい変数をインスタンス変数にセット
        self.root = root
        self.radio_var  = radio_var
        self.listbox_script = listbox_script
        self.list_var = list_var
        self.tv_info = tv_info
    
        #現在の状態をラベルに表示
        self.disp_inout_file()

        root.mainloop()
        
if __name__ == '__main__':
    proc = Process()
    proc.main()
    