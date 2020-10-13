import pickle
import re
import os
import json
import sys
import numpy as np
import pandas as pd
import datetime
path = "/home/mlb/res/stock/twse/json/"
regex = re.compile(r"[12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])")
def check_null(info):
    for key, value in info.items(): #avoid null value
        if value=='NULL' or value=='':
            return False
    return True
def loader(stock_number,filename):
      print(f"Start load data of {stock_number} ...")
      raw_data=[]
      for name in os.listdir(path):
         if(regex.match(name) ):
            with open(os.path.join(path,name)) as f:
                  try:
                     s=json.load(f)[stock_number]
                     if(check_null(s)):
                        s['date'] = ''.join(name[0:10].split('-'))
                        s['year'] = int(name[0:4])
                        s['month'] = int(name[5:7])
                        s['day'] = int(name[8:10])
                        s['week'] = datetime.datetime(s['year'], s['month'], s['day']).weekday()

                        raw_data.append(s)
                  except KeyError:
                     print(f'Can not find the information of {stock_number}')
      if len(raw_data):
         with open(filename+".pickle",'wb') as output:
            df = pd.DataFrame(raw_data).sort_values(by=['date'])
            #df=df.drop(['adj_close'], axis=1)
            df[['adj_close','close','high','low','open']]=df[['adj_close','close','high','low','open']].astype('float64')
            df[['volume','date']]=df[['volume','date']].astype('int')
            df=df.reset_index(drop=True)
            pickle.dump(df,output)
            print(f"End loading.")
      else:
         print("Error: empty data can not generate output file.")

if '__main__' == __name__:
   loader(sys.argv[1],sys.argv[1])