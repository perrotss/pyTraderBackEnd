from ib_insync import *
import pandas as pd
import creds
import numpy as np
import pickle
from helper.delta import CalculateDelta
from helper.deltas import CalculateDeltas
from datetime import datetime, timedelta
import pytz
UTC = pytz.utc
timeZ_Ny = pytz.timezone('America/New_York')
class Bull_Spread2():
    def __init__(self,ib,entry_delta,expirations,rights,qty,action,deltasl):
        self.ib=ib
        self.entry_delta=entry_delta
        self.expirations=expirations
        self.qty=qty
        self.rights=rights
        self.action=action
        self.deltasl=deltasl
        self.open=0
    def closest_value(self,input_list, input_value):
       print(input_value)
       print(input_list)
       if(input_value<0):
            input_value=abs(input_value)
            return min(input_list, key=lambda x:abs(x+input_value))
       else:
            return min(input_list, key=lambda x:abs(x-input_value))
    def find_ticker(self,tickers,contracts,delta):
        try:
            d=[tick.modelGreeks.delta for tick in tickers]
        except:
            tickers=self.ib.reqTickers(contracts)
            self.wait_for_data(tickers)
            print("start")
            opt_prices=[tick.marketPrice() for tick in tickers] #remove on live
            opt_Strikes=[cont.strike for cont in contracts]
            print(opt_prices)
            print(opt_Strikes)
            flag = "PUT" if self.rights == "P" else "CALL"
            print("end")
            p1 = CalculateDeltas(self.ib,flag,self.spx_ticker,tickers,self.expirations,contracts,opt_prices,opt_Strikes)
            d=p1.get_delta()
        print("calculation done")
        dlta=self.closest_value(d,delta)
        for n,i in enumerate(d):
            if(i==dlta):
                print("closest delta",dlta)
                return contracts[n],tickers[n]
    def save_variables(self):
        open=self.open
        try:
            put_option_contract=self.put_option_contract
        except:
            put_option_contract=0
        try:
            opp_contract=self.opp_contract
        except:
            opp_contract=0
        myvar={"open":open,"contract":put_option_contract,"opp_contract":opp_contract}
        pd.DataFrame(data=myvar, index=[0]).to_excel("storage/database.xlsx")
        

    def place_order(self,contract,action):
        order = MarketOrder(action,self.qty)
        trade = self.ib.placeOrder(contract, order)
        while not trade.isDone():
            self.ib.sleep(1)
        print("trade placed successfully")
        return trade,order
    
    def round_to_nearest_5(self,num):
        return round(num / 5) * 5
    def find_opp_strike(self):
        below_price=self.put_option_contract.strike-(creds.Bull_Spread2_below_perc*self.put_option_contract.strike/100)
        self.opp_strike=self.round_to_nearest_5(below_price)
        
    def close_position(self,con):
        positions = self.ib.positions()  # A list of positions, according to IB
        for position in positions:
            if(str(position.contract)==str(con)):
                contract = Contract(conId = position.contract.conId)
                self.ib.qualifyContracts(contract)
                if position.position > 0: # Number of active Long positions
                    action = 'Sell' # to offset the long positions
                elif position.position < 0: # Number of active Short positions
                    action = 'Buy' # to offset the short positions
                else:
                    assert False
                #totalQuantity = abs(position.position)
                totalQuantity=self.qty
                order = MarketOrder(action=action, totalQuantity=totalQuantity)
                trade = self.ib.placeOrder(contract, order)
                print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
                assert trade in self.ib.trades(), 'trade not listed in ib.trades'
    def wait_for_data(self,ticker):
        #for i in range(int((n+10)/10)):
        for tickers in ticker:
            while(True):
                try:
                    #if(tickers.modelGreeks.delta!="nan"):
                        if(tickers.last!="nan"):
                                print(tickers.strike,tickers.close)
                                break        
                except:
                    print("sleeping for 1 seconds <waiting for data>")
                    self.ib.sleep(1)
                    

    def get_model_greeks(self,contract,ticker):
        #self.ib.qualifyContracts(contract)
        #tickers = self.ib.reqMktData(contract)
        tickers=ticker
        self.wait_for_data([tickers])
        print(tickers)
        try:
            if tickers.modelGreeks.delta !="nan":
                delta=(tickers.modelGreeks.delta)
                if delta is not None:
                    return delta
        except:
            flag = "PUT" if self.rights == "P" else "CALL"
            p1 = CalculateDelta(self.ib,flag,self.spx_ticker,tickers,self.expirations,contract)
            delta=(p1.get_delta())
            return delta

    def get_close_time(self):
        
        now=datetime.now(timeZ_Ny)
        next_day = datetime.now(timeZ_Ny) + timedelta(days=1)
        self.next_day_time=next_day.replace(hour=15, minute=50,second=0)
        
    def check_time(self):
        now=datetime.now(timeZ_Ny)
        print("current time is",now)
        print("waiting untill",self.next_day_time)
        if(now>=self.next_day_time):
            return True
        else:
            return False
        
    def stoploss(self,contract,ticker,opp_contract,opp_ticker):
        while True:
            [ticker] = self.ib.reqTickers(contract)

            self.wait_for_data([ticker])
            price = ticker.last
            opp_price=opp_ticker.last
            delta=self.get_model_greeks(contract,ticker)
            spxValue = ticker.marketPrice()
            print(price,spxValue,delta)
            if(price<=creds.sl):
                print("stoploss triggered")
                self.close_position(self.combined_contract)
                #self.close_position(contract)
                #self.close_position(opp_contract)
                break
            elif(delta>=self.deltasl):
                print("stoploss triggered")
                self.close_position(self.combined_contract)
                #self.close_position(contract)
                #self.close_position(opp_contract)
                break
            elif(self.check_time()):
                print("stoploss triggered")
                self.close_position(self.combined_contract)
                #self.close_position(contract)
                #self.close_position(opp_contract)
                break
            else:
                print("stoploss not triggered")
                print(price,spxValue,delta)
            self.ib.sleep(1)
        self.open=0
    def place_combined_order(self,cont,action,opp_cont,opp_action):
        contract = Contract()
        contract.symbol = cont.symbol
        contract.secType = "BAG"
        contract.currency = cont.currency
        contract.exchange = cont.exchange
        leg1 = ComboLeg()
        leg1.conId = cont.conId
        leg1.ratio = 1
        leg1.action = action
        leg1.exchange = cont.exchange
        leg2 = ComboLeg()
        leg2.conId = opp_cont.conId 
        leg2.ratio = 1
        leg2.action = opp_action
        leg2.exchange = opp_cont.exchange
        contract.comboLegs = []
        contract.comboLegs.append(leg1)
        contract.comboLegs.append(leg2)
        self.place_order(contract,self.action)
        return contract

    def main(self):
        #spx = Stock('SPX','ARCA','USD')
        spx = Index('SPX', 'CBOE')
        self.ib.qualifyContracts(spx)
        self.ib.reqMarketDataType(creds.marketdatatype)
        [ticker] = self.ib.reqTickers(spx)
        
        spxValue = ticker.marketPrice()
        if(str(spxValue)=="nan"):  #remove on live
            spxValue=3956
        elif((spxValue)==0):
            spxValue=ticker.close
        print(spxValue)
        self.spx_ticker=ticker
        self.spx_contract=spx
        chains = self.ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
        chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
        strikes = [strike for strike in chain.strikes
        if strike % 5 == 0
        #and strike<=spxValue
        and spxValue - 10 < strike < spxValue + 10 #comment when live
        ]
        expirations = sorted(exp for exp in chain.expirations)[:2]
        if(self.expirations==0):
            expiration=expirations[0]
        else:
            expiration=expirations[1]
        
        right=self.rights
        print(expirations)
        self.Opp_flag="CALL" if self.rights == "P" else "PUT"
        if(self.action=="SELL"):
            self.opp_action="BUY"
        else:
            self.opp_action="SELL"
        put_contracts = [Option('SPX', expiration, strike, right, 'SMART', tradingClass='SPXW')
                #for right in rights
                #for expiration in expirations
                for strike in strikes]
        put_contracts = self.ib.qualifyContracts(*put_contracts)
        put_tickers = self.ib.reqTickers(*put_contracts)
        self.wait_for_data(put_tickers)
        self.put_option_contract,self.put_option_ticker=self.find_ticker(put_tickers,put_contracts,self.entry_delta)
        self.find_opp_strike()

        for i,j in zip(put_contracts,put_tickers):
            print(i.strike,self.opp_strike)
            if(int(i.strike)==int(self.opp_strike)): #change to == when live
                self.opp_contract=i
                self.opp_ticker=j
        self.place_combined_order(self.put_option_contract,self.action,self.opp_contract,self.opp_action)
        #trade,order=self.place_order(self.put_option_contract,self.action)
        #opp_trade,opp_order=self.place_order(self.opp_contract,self.opp_action)
        self.open=1
        self.save_variables()
        self.get_close_time()
        self.stoploss(self.put_option_contract,self.put_option_ticker,self.opp_contract,self.opp_ticker)
        self.save_variables()

