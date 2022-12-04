
import random
import time
import helper.helpers as helpers
from ib_insync import *
import creds
from multiprocessing import Pool
from joblib import Parallel, delayed
ib=IB()
class CalculateDeltas():
    def __init__(self,ib,put_or_call,ticker,ticker_option,dte,con,opt_prices,opt_Strikes):
        self.ib=ib
        self.put_or_call=put_or_call
        self.option_contract=con
        self.ticker=ticker
        self.ticker_option=ticker_option
        self.dte=dte
        self.opt_prices=opt_prices
        self.opt_Strikes=opt_Strikes
    def login(self):
        while True:
            try:
                random_id = random.randint(0, 9999)
                #random_id=0
                ibs=ib.connect('127.0.0.1', creds.port, clientId=random_id)
                print("connected")
                return ibs
                break
            except:
                print("retrying to login")
                time.sleep(1)
                pass
    def isconnected(self,ib):
        if(ib.isConnected()):
            print("connected")
            ibs=ib
        else:
            #random_id = random.randint(0, 9999)
            ibs=self.login()
        return ibs
    def wait_for_data(self,ticker):
        #for i in range(int((n+10)/10)):
        for tickers in ticker:
            while(True):
                try:
                    #if(tickers.modelGreeks.delta!="nan"):
                        
                        if(str(tickers.last)!="nan"):
                                print(tickers)        
                                break
                        else:
                            print("<waiting for data>")
                            self.ib.sleep(1)
                except:
                    print("sleeping for 1 seconds <waiting for data>")
                    self.ib.sleep(1)
    def calculate_delta(self,strike,option_price):
        underlying_last_price= self.ticker.marketPrice()
        if(str(underlying_last_price)=="nan"):  #remove on live
            underlying_last_price=3956
        elif((underlying_last_price)==0):
            underlying_last_price=self.ticker.last
        print(strike,option_price,underlying_last_price)
        days_to_expiration=self.dte + 1
        
        # Calculate Delta
        calculated_delta = helpers.calculate_delta(
            underlying_last_price,
            strike,
            self.risk_free_rate,
            days_to_expiration,
            self.put_or_call,
            None,
            option_price,
        )  
        print(calculated_delta)
        return calculated_delta    
    def get_delta(self):
        self.risk_free_rate = creds.risk_free_rate
        calculated_delta=Parallel(n_jobs=20,require='sharedmem')(delayed(self.calculate_delta)(i,j) for i,j in zip(self.opt_Strikes,self.opt_prices))
        print("delta",calculated_delta)
        return calculated_delta
#p1 = CalculateDelta("1","PUT","20221111","C",3)
#print(p1.get_best_strike())