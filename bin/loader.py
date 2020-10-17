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

def moving_average(data,period):
    return data['close'].rolling(period).mean()
def EMA(data,span):
    return data['close'].ewm(span=span).mean()
def MACD(data):
    data['DIF'] = data['EMA_12'] - data['EMA_26']
    data['DEM'] = data['DIF'].ewm(span=9).mean()
    data['OSC'] = data['DIF'] - data['DEM']
    return data
def KD(data):
    data_df = data.copy()
    data_df['min'] = data_df['low'].rolling(9).min()
    data_df['max'] = data_df['high'].rolling(9).max()
    data_df['RSV'] = (data_df['close'] - data_df['min'])/(data_df['max'] - data_df['min'])
    data_df = data_df.dropna()
    # 計算K
    # K的初始值定為50
    K_list = [50]
    for num,rsv in enumerate(list(data_df['RSV'])):
        K_yestarday = K_list[num]
        K_today = 2/3 * K_yestarday + 1/3 * rsv
        K_list.append(K_today)
    data_df['K'] = K_list[1:]
    # 計算D
    # D的初始值定為50
    D_list = [50]
    for num,K in enumerate(list(data_df['K'])):
        D_yestarday = D_list[num]
        D_today = 2/3 * D_yestarday + 1/3 * K
        D_list.append(D_today)
    data_df['D'] = D_list[1:]
    use_df = pd.merge(data,data_df[['K','D']],left_index=True,right_index=True,how='left')
    return use_df

def RSI(data):
    def cal_U(num):
        if num >= 0:
            return num
        else:
            return 0
    def cal_D(num):
        num = -num
        return cal_U(num)
    
    data['Dif'] = data['close'].diff()
    data['U'] = data['Dif'].apply(cal_U)
    data['D'] = data['Dif'].apply(cal_D)
    data['ema_U'] = data['U'].ewm(span=14).mean()
    data['ema_D'] = data['D'].ewm(span=14).mean()
    data['RS'] = data['ema_U'].div(data['ema_D'])
    data['RSI'] = data['RS'].apply(lambda rs:rs/(1+rs) * 100)
    return data['RSI']

def OBV(data):
    return (data['close']-data['low']).div(data['high']-data['low'])

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
         with open(os.path.join(os.getcwd(),"data",f"{filename}.pickle",),'wb') as output:
            df = pd.DataFrame(raw_data).sort_values(by=['date'])
            df[['adj_close','close','high','low','open']]=df[['adj_close','close','high','low','open']].astype('float64')
            df[['volume','date']]=df[['volume','date']].astype('int')

            #add technical analysis
            df.drop(['date'],inplace=True, axis=1)
            df = KD(df)
            df['MA_5']=moving_average(df,5)
            df['MA_10']=moving_average(df,10)
            df['MA_20']=moving_average(df,20)
            df['MA_60']=moving_average(df,60)
            df['MA_240']=moving_average(df,240)
            df['EMA_12']=EMA(df,12)
            df['EMA_26']=EMA(df,26)
            df = MACD(df)
            df['RSI']=RSI(df)
            df['OBV']=OBV(df)
            #drop NaN and inf
            df.replace([np.inf, -np.inf], np.nan,inplace=True)
            df.dropna(inplace=True)
            df.reset_index(drop=True,inplace=True)
            pickle.dump(df,output)
            print(f"End loading.")
      else:
         print("Error: empty data can not generate output file.")

def reloader(stock_number):
      print(f"Start reload data of {stock_number} ...")
      raw_data=[]
      all_files=sorted(os.listdir(path))
      with open(os.path.join(os.getcwd(),"data",f"{stock_number}.pickle"),'rb') as f:
        df = pickle.load(f)
      last_df=df.iloc[-1]
      last_name=f"{str(int(last_df['year']))}-{str(int(last_df['month']))}-{str(int(last_df['day']))}.json"

      for name in reversed(all_files):
        if(name!=last_name):
            
            with open(os.path.join(path,name)) as f:
                print(name)
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
        else:
            break
      if len(raw_data):
         with open(os.path.join(os.getcwd(),"data",f"{stock_number}.pickle",),'wb') as output:
            new_df = pd.DataFrame(raw_data).sort_values(by=['date'])
            new_df[['adj_close','close','high','low','open']]=new_df[['adj_close','close','high','low','open']].astype('float64')
            new_df[['volume','date']]=new_df[['volume','date']].astype('int')

            #add technical analysis
            new_df.drop(['date'],inplace=True, axis=1)
            print(new_df)
            print(len(df))
            df.drop(['K','D'],inplace=True,axis=1)
            df=df.append(new_df,ignore_index=True)
            print(len(df))
            df = KD(df)
            df['MA_5']=moving_average(df,5)
            df['MA_10']=moving_average(df,10)
            df['MA_20']=moving_average(df,20)
            df['MA_60']=moving_average(df,60)
            df['MA_240']=moving_average(df,240)
            df['EMA_12']=EMA(df,12)
            df['EMA_26']=EMA(df,26)
            df = MACD(df)
            df['RSI']=RSI(df)
            df['OBV']=OBV(df)
            #drop NaN and inf
            df.replace([np.inf, -np.inf], np.nan,inplace=True)
            df.dropna(inplace=True)
            df.reset_index(drop=True,inplace=True)
            #print(df.iloc[-1])
            pickle.dump(df,output)
            print(f"End reloading.")
      else:
          print(f"Nothing to update for {stock_number}")

if '__main__' == __name__:

    if(os.path.isfile(os.path.join(os.getcwd(),"data",f'{sys.argv[1]}.pickle'))):
        reloader(sys.argv[1])
    else:  
        loader(sys.argv[1],sys.argv[1])