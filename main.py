from ib_insync import *
import pandas as pd
import time
from modules.bull_put_spread import Bull_Spread
import creds
import random
from modules.bull_put_spread2 import Bull_Spread2

from modules.naked_call import Naked_Call
util.startLoop()  # uncomment this line when in a notebook
import numpy as np
import multiprocessing
import os
from datetime import datetime
import pickle
import pytz
import helper.helpers as helpers
import re
UTC = pytz.utc
timeZ_Ny = pytz.timezone('America/New_York')
ib=IB()

class Strategies():
    def __init__(self) -> None:
        pass
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
    def get_random():
        random_id = random.randint(0, 9999)
        return random_id

    def close_position(self,ib,con):
        m = re.search(r"conId=(\d+)", con)
        if m:
            conid=(m.group(1))
        positions = ib.positions()  # A list of positions, according to IB
        for position in positions:
            if(str(position.contract.conId)==str(conid)):
                contract = Contract(conId = position.contract.conId)
                ib.qualifyContracts(contract)
                if position.position > 0: # Number of active Long positions
                    action = 'Sell' # to offset the long positions
                elif position.position < 0: # Number of active Short positions
                    action = 'Buy' # to offset the short positions
                else:
                    assert False
                #totalQuantity = abs(position.position)
                totalQuantity=creds.Bull_Spread2_qty
                order = MarketOrder(action=action, totalQuantity=totalQuantity)
                trade = ib.placeOrder(contract, order)
                print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
                assert trade in ib.trades(), 'trade not listed in ib.trades'
            else:
                print(position.contract.conId)
                print(conid)
    def prevday_position(self,ib):
        df=pd.read_excel("storage/database.xlsx")
        open=df["open"].to_list()[0]
        contract=df["contract"].to_list()[0]
        opp_contract=df["opp_contract"].to_list()[0]
        if(open==1):
            print("closing open positions")
            self.close_position(ib,contract)
            self.close_position(ib,opp_contract)
        else:
            print("there were no open positions yesterday")
    def get_risk_free_rate(self):
        while True:
            try:
                creds.risk_free_rate = helpers.get_risk_free_rate()
                break
            except:
                print("exception getting risk free rate . cheak your internet")
                pass
    def Naked_Call_Main(self):
        ib=self.login()
        now=datetime.now(timeZ_Ny)
        cur_time=now.time()
        start_time=(now.replace(hour=creds.Naked_Call_start_hour,minute=creds.Naked_Call_start_minutes,second=0,microsecond=0)).time()
        print(cur_time,start_time)
        while True:
            now=datetime.now(timeZ_Ny)
            cur_time=now.time()
            print(cur_time,start_time)
            if(cur_time>=start_time):
                if(not self.isconnected(ib)):
                    ib=self.login()
                p1 = Naked_Call(ib,creds.Naked_Call_entry_delta,creds.Naked_Call_dte,"C",creds.Naked_Call_qty,creds.Naked_Call_action,creds.Naked_Call_stop_loss_delta)
                p1.main()
            #else:
            #    print("current time is ",cur_time," Naked call is waiting untill",start_time)
            time.sleep(1)
    def Bull_Spread_Main(self):
        ib=self.login()
        now=datetime.now(timeZ_Ny)
        cur_time=now.time()
        start_time=(now.replace(hour=creds.Bull_Spread_start_hour,minute=creds.Bull_Spread_start_minutes,second=0,microsecond=0)).time()
        while True:
            now=datetime.now(timeZ_Ny)
            cur_time=now.time()
            if(cur_time>=start_time):
                if(not self.isconnected(ib)):
                    ib=self.login()
                self.prevday_position(ib)
                p2= Bull_Spread(ib,creds.Bull_Spread_entry_delta,creds.Bull_Spread_dte,"P",creds.Bull_Spread_qty,creds.Bull_Spread_action,creds.Bull_Spread_stop_loss_delta)
                p2.main() 
            #else:
            #    print("current time is ",cur_time," Bull Spread 1 is waiting untill",start_time)
            time.sleep(1)
    def Bull_Spread_Main2(self):
        ib=self.login()
        now=datetime.now(timeZ_Ny)
        cur_time=now.time()
        start_time=(now.replace(hour=creds.Bull_Spread2_start_hour,minute=creds.Bull_Spread2_start_minutes,second=0,microsecond=0)).time()
        while True:
            now=datetime.now(timeZ_Ny)
            cur_time=now.time()
            if(cur_time>=start_time):
                if(not self.isconnected(ib)):
                    ib=self.login()
                p3= Bull_Spread2(ib,creds.Bull_Spread2_entry_delta,creds.Bull_Spread2_dte,"P",creds.Bull_Spread2_qty,creds.Bull_Spread2_action,creds.Bull_Spread2_stop_loss_delta) #change when live
                p3.main()
                break 
            #else:
                print("current time is ",cur_time," Bull Spread 2 is waiting untill",start_time)
            time.sleep(1)
        
    def main(self):
        p1 = multiprocessing.Process(target=self.Naked_Call_Main)
        p2 = multiprocessing.Process(target=self.Bull_Spread_Main)
        p3 = multiprocessing.Process(target=self.Bull_Spread_Main2)
        p1.start()
        p2.start()
        p3.start()
        #ib=self.login(1)
        #p1 = Naked_Call(ib,0.1,0,"C",3,"SELL",45)
        #p1.main()
        #p2= Bull_Spread2(ib,0.16,0,"P",3,"SELL",45)
        #p2.main()
if __name__ == '__main__':       
    start=Strategies()
    start.get_risk_free_rate()
    start.Bull_Spread_Main2()
    #start.Naked_Call_Main()
    #start.main()