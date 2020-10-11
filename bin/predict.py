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
   path = "/home/mlb/res/stock/twse/json/"
   date = sys.argv[1].split('-')
   s=datetime.datetime(int(date[0]),int(date[1]),int(date[2]))
   pre_data = []
   n = 1
   while(len(pre_data)<7 and n<100):
      d = (s-datetime.timedelta(days=n)).strftime('%Y%m%d')
      try:
         with open(path+d[0:4]+'-'+d[4:6]+'-'+d[6:8]+'.json') as f:
            try:
               stock = json.load(f)['0051']
               if(check_null(stock)):
                  stock['date'] = d
                  pre_data.insert(0,stock)
            except KeyError:
               pass

      except FileNotFoundError:
         pass
      finally:
         n+=1
   if(len(pre_data)!=7):
      print("Wrong length of feature")
   else:
      df = pd.DataFrame(pre_data)
      print(df)
      #print(df['high'].values[:])
      