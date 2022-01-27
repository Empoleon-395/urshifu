import pandas as pd
import numpy as np
import collections
from sklearn.preprocessing import scale
import optuna.integration.lightgbm as lgb

from mkdata import mkdata

poke_info = pd.read_csv("./data/poke_info.csv")
poke_info["id"]=[list(poke_info["name"].unique()).index(i)+1 for i in poke_info["name"]]

class make_prediction:
    def __init__(self,poke_list):
        self.poke_list = poke_list
        self.set_data()

    def set_data(self):
        self.se = pd.Series(dtype = "float64")
        for i in range(1,len(self.poke_list)+1):
            a = pd.Series({"poke"+str(i):poke_info[poke_info["name_h"]==self.poke_list[i-1]]["id"].reset_index(drop =True)[0],"form"+str(i):poke_info[poke_info["name_h"]==self.poke_list[i-1]]["form"].reset_index(drop =True)[0]})
            self.se = pd.concat([self.se,a])
        mki = mkdata(self.se)
        self.test_x = mki.get_df()

    def predict(self):
        test_x = self.test_x.drop(list(self.test_x.columns[self.test_x.columns.str.startswith("type")]),axis =1)
        bst = lgb.Booster(model_file='./models/optunalgbm.txt')
        ypred = bst.predict(test_x, num_iteration=bst.best_iteration)
        return ypred
