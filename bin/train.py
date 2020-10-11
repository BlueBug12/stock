import pickle
import re
import os
import json
import sys
import numpy as np
import pandas as pd
from sklearn.utils import shuffle
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import GradientBoostingRegressor

path = "/home/mlb/res/stock/twse/json/"
regex = re.compile(r"[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])")
def check_null(info):
    for key, value in info.items(): #avoid null value
        if value=='NULL' or value=='':
            return False
    return True
class ml_model():
   def __init__(self,stock_number,reload=False):
      self.stock_number = stock_number
      self.raw_data=[]
      self.df=None
      if(reload):
         self.loader(stock_number)
      else:
         try:
            with open(stock_number+".pickle",'rb') as f:
               self.df = pickle.load(f)
         except FileNotFoundError:
            self.loader(stock_number)

   
   def loader(self,filename):
      print(f"Start load data of {self.stock_number} ...")
      for name in os.listdir(path):
         if(regex.match(name)):
            with open(os.path.join(path,name)) as f:
                  try:
                     s=json.load(f)[self.stock_number]
                     if(check_null(s)):
                        s['date'] = ''.join(name[0:10].split('-'))
                        self.raw_data.append(s)
                  except KeyError:
                     print(f'Can not find the information of {self.stock_number} in file {self.stock_number}')
      if len(self.raw_data):
         with open(filename+".pickle",'wb') as output:
            df = pd.DataFrame(self.raw_data).sort_values(by=['date'])
            df.drop(['adj_close'], axis=1)
            df[['close','high','low','open']]=df[['close','high','low','open']].astype('float64')
            df[['volume','date']]=df[['volume','date']].astype('int')
            self.df=df.reset_index(drop=True)
            pickle.dump(self.df,output)
            print(f"End loading.")
      else:
         print("Error: empty data can not generate output file.")

   def extract_training_data(self,feature,back,ahead=1):
      print(self.df.info())
      data_x=[]
      data_y=[]
      
      for i in range(back,len(self.df)-(ahead)):
         batch=self.df.iloc[i-back:i]
         data_x.append(list(batch[feature].values[:])+list(batch['volume'].values[:]))
         data_y.append(self.df[feature][i+ahead-1])

      return data_x,data_y

   def write_model(self,filename,clf):
      with open(filename+".sav","wb") as out_model:
         pickle.dump(clf,out_model)
   def test_model(self,test_x, test_y,clf):
      print(clf.score(test_x, test_y))
   def show(self):
      print(self.df)
   def train_model(self,feature,back,ahead=1,test_size=0.33,random_state=1,write=False):
      data_x,data_y = self.extract_training_data(feature,back,ahead)
      data_X,data_Y= shuffle(data_x,data_y, random_state=random_state)
      train_x, test_x,train_y,test_y = train_test_split(data_X, data_Y, test_size=test_size, random_state=random_state)
      clf = Pipeline([
         ('scl', StandardScaler()),
         ('pca', PCA(n_components=5)),
         #('clf',SVR())
         ('clf',GradientBoostingRegressor())
         
         #('clf', RandomForestRegressor(n_estimators=1000,max_depth=8))
      ])

      clf.fit(train_x, train_y)
      print(clf.score(test_x, test_y))
      print(mean_squared_error(clf.predict(test_x),test_y))
      #self.test_model(test_x, test_y,clf)
      if(write):
         self.write_model(f"{feature}_{str(back)}_{str(ahead)}_{self.stock_number}",clf)


if '__main__' == __name__:
   m = ml_model(sys.argv[4])
   m.train_model(feature=sys.argv[1],back=int(sys.argv[2]),ahead=int(sys.argv[3]),write=True)
   #m.show()
