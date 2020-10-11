import pickle
import sys
import re
import os
import json
import datetime
import pandas as pd

def check_null(info):
   for key, value in info.items(): #avoid null value
      if value=='NULL' or value=='':
         return False
   return True
if __name__ == '__main__':
   feature = sys.argv[2]
   back = int(sys.argv[3])
   ahead = int(sys.argv[4])
   stock_n = sys.argv[5]

   path = "/home/mlb/res/stock/twse/json/"
   date = sys.argv[1].split('-')
   s=datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
   pre_data = []
   n = 1
   while(len(pre_data)<back and n<100):
      d = (s-datetime.timedelta(days=n)).strftime('%Y%m%d')
      try:
         with open(path+d[0:4]+'-'+d[4:6]+'-'+d[6:8]+'.json') as f:
            try:
               stock = json.load(f)[stock_n]
               if(check_null(stock)):
                  stock['date'] = d
                  pre_data.insert(0,stock)
            except KeyError:
               pass

      except FileNotFoundError:
         pass
      finally:
         n+=1
   if(len(pre_data)!=back):
      print("Wrong length of feature")
   else:
      df = pd.DataFrame(pre_data)
      print(df)
      with open(f"{feature}_{str(back)}_{ahead}_{stock_n}.sav",'rb') as f:
         clf = pickle.load(f)
         #print(df[feature].values[:]+df['volume'].values[:])
         print(f'{feature} price of {stock_n}')
         #+list(batch['volume'].values[:])
         print(clf.predict([list(df[feature].values[:])+list(df['volume'].values[:])]))
      #print(df['high'].values[:])
      