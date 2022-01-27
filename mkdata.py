import pandas as pd
import numpy as np
import collections
from sklearn.preprocessing import scale
from pokepoke import poke
from pokem import plot_poke
a = plot_poke("./")


poke_data = poke()
poke_info = pd.read_csv("./data/poke_info.csv")
move_df = pd.read_csv("./data/move_info.csv")
poke_info["id"]=[list(poke_info["name"].unique()).index(i)+1 for i in poke_info["name"]]

class mkdata:
    def __init__(self,ofive):
        self.ofive = ofive
        self.get_ty()
        self.get_m()

    def get_m(self):
        poke_info = poke()
        data = self.ofive
        temp_df = pd.DataFrame()
        for i in range(1,7):
            id = data["poke"+str(i)]
            if id == 892:
                continue
            form = data["form"+str(i)]
            waza_list = a.poke_data[str(id)][str(form)]["temoti"]["waza"]
            move_type = [move_df[move_df["name"]==poke_info.poke_move[int(i["id"])]]["type"].reset_index(drop=True)[0] for i in waza_list]
            move_clas = [move_df[move_df["name"]==poke_info.poke_move[int(i["id"])]]["class"].reset_index(drop=True)[0] for i in waza_list]
            m_ty_df = pd.DataFrame(columns=poke_info.poke_type)
            m_ty_df = scale(pd.concat([m_ty_df,pd.DataFrame((dict(collections.Counter(move_type))),index=[i,])]).fillna(0),axis = 1)
            m_ty_df = pd.DataFrame(m_ty_df)
            cl_name = ["mtype"+str(j) for j in range(len(poke_info.poke_type))]
            m_ty_df = m_ty_df.set_axis(cl_name,axis=1)
            st_dic= dict(collections.Counter(move_clas))
            try:
                st_dic["ph"] = st_dic["物理"]
                del st_dic["物理"]
            except:
                print("nasi")
            try:
                st_dic["sp"] = st_dic["特殊"]
                del st_dic["特殊"]
            except:
                print("nasi")
            try:
                st_dic["sta"] = st_dic["変化"]
                del st_dic["変化"]
            except:
                print("nasi")
            m_cl_df = pd.DataFrame(columns=["ph","sp","sta"])
            m_cl_df = scale(pd.concat([m_cl_df,pd.DataFrame((st_dic),index=[i,])]).fillna(0),axis = 1)
            m_cl_df = pd.DataFrame(m_cl_df)
            m_cl_df = m_cl_df.set_axis(["ph","sp","sta"],axis=1)
            rt_df = pd.merge(m_ty_df,m_cl_df,left_index=True,right_index=True)
            temp_df = pd.concat([temp_df,rt_df])
        self.df2 = pd.DataFrame(np.sum(temp_df,axis=0)).T

    def get_ty(self):
        test = self.ofive
        data = pd.DataFrame()
        for j in range(1,7):
            data_1 = poke_info[poke_info["id"]==test["poke"+str(j)]].reset_index(drop = True)
            data = pd.concat([data,data_1[data_1["form"]==test["form"+str(j)]]])
        data = data.reset_index(drop = True)
        data = data.drop(int(data[data["name"]=="ウーラオス"].index.values)).reset_index(drop=True)
        ty_list = list(data["type_1"])
        ty_list.extend(list(data["type_2"]))
        type_df = pd.DataFrame(columns=poke_data.poke_type)
        ty_sc = scale(pd.concat([type_df,pd.DataFrame((dict(collections.Counter(ty_list))),index=[0,])]).fillna(0),axis = 1)
        ty_df = pd.DataFrame()
        for j,n in enumerate(ty_sc[0]):
            ty_df["type"+str(j)]=[n]
        r_df = pd.DataFrame(scale(np.sum(data)[["H","A","B","C","D","S"]])).T.set_axis(["H","A","B","C","D","S"],axis=1)
        self.rt_df = pd.merge(r_df,ty_df, left_index=True,right_index=True)
        
        self.df1 =  self.rt_df

    def get_df(self):
        df = pd.merge(self.df1,self.df2,left_index=True,right_index=True)
        return df