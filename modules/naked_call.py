from ib_insync import *
import pandas as pd
import creds
import numpy as np

from helper.delta import CalculateDelta
from helper.deltas import CalculateDeltas

class Naked_Call():
    def __init__(self,ib,entry_delta,expirations,rights,qty,action,deltasl):
        self.ib=ib
        self.entry_delta=entry_delta
        self.expirations=expirations
        self.qty=qty
        self.rights=rights
        self.action=action
        self.deltasl=deltasl
    def closest_value(self,input_list, input_value):
       return min(input_list, key=lambda x:abs(x-input_value))
    def find_ticker(self,tickers,contracts,delta):

        try:
            d=[tick.modelGreeks.delta for tick in tickers]
        except:
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

    def place_order(self,contract):
        if(self.action=="SELL"):
            action="BUY"
        else:
            action="SELL"
        order = MarketOrder(self.action,self.qty)
        trade = self.ib.placeOrder(contract, order)
        #while not trade.isDone():
        #    self.ib.sleep(1)
        print("trade placed successfully")
        return trade,order
    def close_position(self,con):
        positions = self.ib.positions()  # A list of positions, according to IB
        for position in positions:
            if(position.contract==con):
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
    def wait_for_data(self,ticker,contract):
        #for i in range(int((n+10)/10)):
        for tickers,contracts in zip(ticker,contract):
            while(True):
                try:
                    #if(tickers.modelGreeks.delta!="nan"):
                        if(tickers.last!="nan"):
                                print(tickers)
                                break        
                except:
                    print("sleeping for 1 seconds <waiting for data>")
                    self.ib.sleep(1)
                    
                #print(tickers)
                #[tickers] = self.ib.reqTickers(contracts)
        
                    

    def get_model_greeks(self,contract,ticker):
        #self.ib.qualifyContracts(contract)
        #tickers = self.ib.reqMktData(contract)
        tickers=ticker
        self.wait_for_data([tickers],[contract])
        #print(tickers)
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

    def stoploss(self,contract,ticker,trade,order):
        while True:
            
            [ticker] = self.ib.reqTickers(contract)
            self.wait_for_data([ticker],[contract])
            delta=self.get_model_greeks(contract,ticker)
            spxValue = ticker.marketPrice()
            print(spxValue,delta)
            if(spxValue<=creds.sl):
                self.close_position(contract)
                break
            elif(delta>=self.deltasl):
                self.close_position(contract)
                break
            print("stoploss not triggered")
            self.ib.sleep(1)


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
            spxValue=ticker.last
        print(spxValue)
        self.spx_ticker=ticker
        self.spx_contract=spx
        chains = self.ib.reqSecDefOptParams(spx.symbol, '', spx.secType, spx.conId)
        chain = next(c for c in chains if c.tradingClass == 'SPXW' and c.exchange == 'SMART')
        strikes = [strike for strike in chain.strikes
        if strike % 5== 0
        #and strike>=spxValue
        #and spxValue - 2000 < strike < spxValue + 2000 #comment when live
        ]
        expirations = sorted(exp for exp in chain.expirations)[:2]
        if(self.expirations==0):
            expiration=expirations[0]
        else:
            expiration=expirations[1]
        
        right=self.rights
        print(expirations)
        contracts = [Option('SPX', expiration, strike, right, 'SMART', tradingClass='SPXW')
                #for right in rights
                #for expiration in expirations
                for strike in strikes]
        contracts = self.ib.qualifyContracts(*contracts)
        tickers = self.ib.reqTickers(*contracts)
        self.wait_for_data(tickers,contracts)
        contract,tickero=self.find_ticker(tickers,contracts,self.entry_delta)
        trade,order=self.place_order(contract)
        self.stoploss(contract,tickero,trade,order)