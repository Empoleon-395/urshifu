import subprocess
import ast
from turtle import color
import matplotlib.pyplot as plt
import japanize_matplotlib
import pandas as pd
import numpy as np
import datetime
import math
import pokepoke

class plot_poke:
    def __init__(self,filename,season=None):
        self.filename = filename
        self.season = season
        self.download_data()
        self.load_data()
        self.dt_now = datetime.datetime.now()

    def run(self,name,form):
        self.name = name
        self.form = form
        self.poke_stats = None
        self.poke_infom = None
        self.poke_move_df = None
        try:
            self.serch()
            self.culc()
            self.plot()
        except:
            try:
                self.culc()
                self.plot()
            except:
                self.err_plot()

    def download_data(self):
        cmd = '''
        curl 'https://api.battle.pokemon-home.com/cbd/competition/rankmatch/list' \
        -H 'accept: application/json, text/javascript, */*; q=0.01' \
        -H 'countrycode: 304' \
        -H 'authorization: Bearer' \
        -H 'langcode: 1' \
        -H 'user-agent: Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36' \
        -H 'content-type: application/json' \
        -d '{"soft":"Sw"}'
        '''
        res = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell=True)
        s_data = ast.literal_eval(res.stdout.decode())
        
        if self.season is None:
            s_dic = s_data["list"][list(s_data["list"].keys())[0]]
            self.season = len(list(s_data["list"].keys()))
        else:
            season = self.season
            s_dic = s_data["list"][list(s_data["list"].keys())[26-season]]
        id = list(s_dic.keys())[1]
        rst = s_dic[list(s_dic.keys())[1]]["rst"]
        ts2 = s_dic[list(s_dic.keys())[1]]["ts2"]
        self.poke_data={}
        for i in range(5):
            cmd = '''
            curl -XGET 'https://resource.pokemon-home.com/battledata/ranking/{'''+str(id)+'''}/{'''+str(rst)+'''}/{'''+str(ts2)+'''}/pdetail-{'''+str(i+1)+'''}'  \
                    -H 'user-agent: Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Mobile Safari/537.36'  \
                    -H 'accept: application/json'
            '''
            res = subprocess.run(cmd,stdout = subprocess.PIPE, stderr = subprocess.PIPE,shell=True)
            self.poke_data.update(ast.literal_eval(res.stdout.decode()))

    def load_data(self):
        self.poke = pokepoke.poke()
        self.move_df = pd.read_csv("./data/move_info.csv")
        self.poke_info = pd.read_csv("./data/poke_info.csv")

    def serch(self):
        move_list = {}
        for i in range(len(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["waza"])):
            move_list[self.poke.poke_move[int(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["waza"][i]["id"])]]=(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["waza"][i]["val"])
        item_list = {}
        for i in range(len(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["motimono"])):
            item_list[self.poke.poke_item[int(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["motimono"][i]["id"])]]=(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["motimono"][i]["val"])
        powe_list={}
        for i in range(len(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["tokusei"])):
            powe_list[self.poke.poke_powe[int(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["tokusei"][i]["id"])]]=(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["tokusei"][i]["val"])
        pers_list = {}
        for i in range(len(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["seikaku"])):
            pers_list[self.poke.poke_pers[int(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["seikaku"][i]["id"])]]=(self.poke_data[str(self.poke.poke_name.index(self.name)+1)][self.form]["temoti"]["seikaku"][i]["val"])
        self.poke_stats = {"name":self.name,"pers":pers_list,"powe":powe_list,"move":move_list,"item":item_list}
        self.poke_move_df = self.move_df[self.move_df["name"].isin(list(self.poke_stats["move"].keys()))].merge(pd.DataFrame({"name":list(self.poke_stats["move"].keys()),"ratio":np.array(list(self.poke_stats["move"].values())).astype("float64")})).sort_values("ratio").reset_index(drop=True)
        
    def culc(self):
        t_df = self.poke_info[self.poke_info["name"]==self.name]
        self.poke_infom = t_df[t_df["form"]==int(self.form)]
        speed = self.poke_infom["S"].reset_index(drop = True).loc[0]
        self.scarf_best = math.floor(((speed*2+31+252/4)/2+5)*1.1*1.5)
        self.best = math.floor(((speed*2+31+252/4)/2+5)*1.1)
        self.better = math.floor(((speed*2+31+252/4)/2+5))
        self.scarf_better = math.floor(((speed*2+31+252/4)/2+5)*1.5)
        self.normal = math.floor(((speed*2+31+0/4)/2+5))
        self.worse = math.floor(((speed*2+31+0/4)/2+5)*0.9)
        self.worst = math.floor(((speed*2+0+0/4)/2+5)*0.9)

    def plot(self):
        fig, axes = plt.subplots(2, 3, tight_layout=True,dpi = 80,figsize = [15,10],facecolor="white")
        wedgeprops={"edgecolor":"black", "width":0.55}
        fig.suptitle(str(self.poke_infom["name_h"].reset_index(drop = True)[0]),size = 25)
        try:
            axes[1,0].set_title("性格",x=0.5,y=0.45,size = 18)
            x = np.array(list(self.poke_stats["pers"].values())).astype("float64")[np.array(list(self.poke_stats["pers"].values())).astype("float64")>1.5]
            label = list(self.poke_stats["pers"].keys())[0:len(x)]
            axes[1,0].pie(x,labels=label,counterclock=False, startangle=90,autopct="%1.1f%%",rotatelabels = True, wedgeprops=wedgeprops)
        except:
            axes[1,0].set_title("性格",size = 18)
            axes[1,0].text(0.5,0.5,"ランクマッチで使用されていないか\n解禁されていません",size = 12,horizontalalignment="center")
            axes[1,0].axis("off")
        axes[1,1].set_title("持ち物",size = 18)
        try:
            x = np.array(list(self.poke_stats["item"].values())).astype("float64")[::-1]
            label = np.array(list(self.poke_stats["item"].keys()))[::-1]
            b3 = axes[1,1].barh(label,x)
            axes[1,1].set_xlim([0,110])
            axes[1,1].bar_label(b3)
        except:
            axes[1,1].text(0.5,0.5,"ランクマッチで使用されていないか\n解禁されていません",size = 12,horizontalalignment="center")
            axes[1,1].axis("off")
        # axes[1,1].set_title("持ち物",x=0.5,y=0.45,size = 18)
        # x = np.array(list(self.poke_stats["item"].values())).astype("float64")
        # label = list(self.poke_stats["item"].keys())[0:len(x)]
        # axes[1,1].pie(x,labels=label,counterclock=False, startangle=90,autopct="%1.1f%%",rotatelabels = True, wedgeprops=wedgeprops)
        try:
            axes[1,2].set_title("特性",x=0.5,y=0.45,size = 18)
            x = np.array(list(self.poke_stats["powe"].values())).astype("float64")[np.array(list(self.poke_stats["powe"].values())).astype("float64")>1.5]
            label = list(self.poke_stats["powe"].keys())[0:len(x)]
            axes[1,2].pie(x,labels=label,counterclock=False, startangle=90,autopct="%1.1f%%",rotatelabels = True, wedgeprops=wedgeprops)
        except:
            axes[1,2].set_title("特性",size = 18)
            axes[1,2].text(0.5,0.5,"ランクマッチで使用されていないか\n解禁されていません",size = 12,horizontalalignment="center")
            axes[1,2].axis("off")
        # axes[1,1].set_title("わざ",x=0.5,y=0.45,size = 18)
        # x = np.array(list(poke_stats["move"].values())).astype("float64")[np.array(list(poke_stats["move"].values())).astype("float64")>1.5]
        # label = list(poke_stats["move"].keys())[0:len(x)]
        # axes[1,1].pie(x,labels=label,counterclock=False, startangle=90,autopct="%1.1f%%",rotatelabels = True, wedgeprops=wedgeprops)
        axes[0,1].set_title("技構成",size = 18)
        try:
            cr = [self.poke.ty_color[j] for j in [self.poke.poke_type.index(i) for i in self.poke_move_df["type"]]]
            b0 = axes[0,1].barh(self.poke_move_df["name"],self.poke_move_df["ratio"],color =cr)
            axes[0,1].set_xlim([0,115])
            axes[0,1].bar_label(b0)
        except:
            axes[0,1].text(0.5,0.5,"ランクマッチで使用されていないか\n解禁されていません",size = 12,horizontalalignment="center")
            axes[0,1].axis("off")
        x = ["S","D","C","B","A","H"]
        y = self.poke_infom[["S","D","C","B","A","H"]].reset_index(drop=True).loc[0]
        b1 = axes[0,0].barh(x,y)
        axes[0,0].set_xlim([0,260])
        axes[0,0].bar_label(b1)
        axes[0,0].set_title("種族値",size = 18)
        x = ["最遅","下降","無振","準速","準速スカーフ","最速","最速スカーフ"]
        y = [self.worst,self.worse,self.normal,self.better,self.scarf_better,self.best,self.scarf_best]
        b1 = axes[0,2].barh(x,y)
        axes[0,2].set_xlim([0,420])
        axes[0,2].bar_label(b1)
        axes[0,2].set_title("素早さ実数値",size = 18)
        plt.gcf().text(0,0.95,str(self.dt_now)+"更新")
        plt.gcf().text(0.8,0.95,"シーズン"+str(self.season))
        plt.savefig(self.filename)
    
    def err_plot(self):
        fig, axes = plt.subplots(1, 1, tight_layout=True,dpi = 100,figsize = [5,5],facecolor="white")
        axes.text(0.5,0.5,"この名前のポケモンは存在しないかバグが発生しています。\nポケモンの名前を確認し、バグの場合は連絡してください。",size = 18,horizontalalignment="center",color = "red")
        axes.text(0.5,0.1,"連絡先\naaa@gmail.com",size = 18,horizontalalignment="center",color = "blue")
        axes.axis("off")
        plt.savefig(self.filename)