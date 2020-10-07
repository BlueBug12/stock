import sys
import re
import os
import json
import numpy as np
#print('Number of arguments:',len(sys.argv))
#print('Argument List:' ,str(sys.argv))
def data_feature(info):
    d=np.array([info['open'],info['close'],info['volume']])
    return d

def data_parser(path,file_name,stocks):
    regex = re.compile(r"([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]))")
    match = regex.match(file_name)
    if match:        
        try:
            with open(path+sys.argv[1]+'.json') as f:
                json_format = json.load(f)
                result = []
                for number in stocks:
                    try:
                        result.append(data_feature(json_format[number]))                      
                    except KeyError:
                        print("Can not find the information about",number)
                print(np.array(result))
        except FileNotFoundError:
            print("Can not find "+sys.argv[1]+'.json')
        

    else:
        print("Invalid argument")
if __name__ == '__main__':
    path = "../../../../res/stock/twse/json/"
    stocks=["0050","0051","0052"]
    data_parser(path,sys.argv[1],stocks)