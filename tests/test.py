from ib_insync import *
import sys


ib=IB()
a = [-5,-1,1,5]
n=min(range(len(a)), key=lambda i: abs(a[i]-2))
print(a[n])



"""
# SuperFastPython.com
# example of a parallel for loop with multiple arguments
from time import sleep
from random import random
from multiprocessing import Pool
 
# task to execute in another process
def task(arg1, arg2, arg3):
    # generate a value between 0 and 1
    value = random()
    # block for a fraction of a second to simulate work
    while True:
        print(value)
    # return the generated value
    return value
 
# entry point for the program
if __name__ == '__main__':
    # create the process pool
    with Pool() as pool:
        # prepare arguments
        items = [(i, i*2, i*3) for i in range(10)]
        # call the same function with different data in parallel
        for result in pool.starmap(task, items):
            # report the value to show progress
            print(result)
"""
"""
import pickle
import pandas as pd
def save_variables():
        open=0
        myvar={"open":open ,"close":0}
        pd.DataFrame(data=myvar, index=[0]).to_excel("storage/database.xlsx")
        save_variables()
# a="Ticker(contract=Option(conId=593342052, symbol='SPX', lastTradeDateOrContractMonth='20221114', strike=3860.0, right='C', multiplier='100', exchange='SMART', currency='USD', localSymbol='SPXW  221114C03860000', tradingClass='SPXW'))"
#print(a.contract)

import mibian
c = mibian.BS([8572, 8700, 0, 0], callPrice= 616.05)
print(c.impliedVolatility)
c = mibian.BS([8572, 8700, 0, 0], volatility = c.impliedVolatility)
print(c.callPrice)
print(c.callDelta)
print(c.callTheta)
print(c.vega)
print(c.gamma)
"""