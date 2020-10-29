import json
import os
import sys
import numpy as np
path = "/home/mlb/res/stock/twse/json/"
def all_price_r(num,step,floor,ceil):
    
    result = []
    if(num+2*step<=ceil):
        result+=all_price_r(round(num+step,2),step,floor,ceil)
    result += [[round(num-step,2),round(num+step,2)]]
    return result

def all_price_l(num,step,floor,ceil):
    result = []
    if(num-2*step>=floor):
        result+=all_price_l(round(num-step,2),step,floor,ceil)
    result += [[round(num-step,2),round(num+step,2)]]
    return result

def reloader(stock_number,profit):
    raw_data=[]
    all_files=sorted(os.listdir(path))
    print(all_files[-1])
    with open(os.path.join(path,all_files[-1])) as f:
        close = float(json.load(f)[stock_number]['close'])
        step = 0
        if close > 1000:
            step = 5
        elif close >= 500:
            step = 1
        elif close >= 100:
            step = 0.5
        elif close >= 50:
            step = 0.1
        elif close >= 10:
            step = 0.05
        else:
            step = 0.01
        floor = close
        ceil = close
        profit/=2
        while floor-step>=close*(0.9):
            floor = round(floor - step,2)
        while ceil+step<=close*(1.1):
            ceil = round(ceil + step,2)
        n = close
        while n+step<=close*(1+profit):
            n = round(n + step,2)
        print('ceil',ceil)
        print('floor',floor)
        print('close',close)
        print('step',round(n-close,2))
        result = all_price_l(close,round(n-close,2),floor,ceil)+all_price_r(close,round(n-close,2),floor,ceil)
        return sorted(result)
        #print(sorted(result))
if '__main__' == __name__:
   stocks = {'1526':0.02,'2454':0.01,'2344':0.02,'3481':0.025}
   decision_set = []
   for number, profit in stocks.items():
      price = reloader(number,profit)
      for i in range(len(price)):
         curr_decision = {
            "code": number,
            "life": 1,
            "type": "buy",
            "weight": 1,
            "open_price": price[i][0],
            "close_high_price": price[i][1],
            "close_low_price": price[i][0]
            }
         decision_set.append(curr_decision)
   if not os.path.exists('../commit/'):
      os.makedirs('../commit/')
   json.dump(decision_set, open(f'../commit/{sys.argv[1]}_{sys.argv[1]}.json', 'w'), indent=4)