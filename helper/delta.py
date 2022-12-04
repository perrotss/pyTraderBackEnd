
import helper.helpers as helpers
from ib_insync import *
import creds
class CalculateDelta():
    def __init__(self,ib,put_or_call,ticker,ticker_option,dte,con):
        self.ib=ib
        self.put_or_call=put_or_call
        self.option_contract=con
        self.ticker=ticker
        self.ticker_option=ticker_option
        self.dte=dte
    def wait_for_data(self,ticker):
        #for i in range(int((n+10)/10)):
        for tickers in ticker:
            while(True):
                try:
                    #if(tickers.modelGreeks.delta!="nan"):
                        print(tickers)
                        if(str(tickers.last)!="nan"):
                                
                                break
                        else:
                            print("<waiting for data>")
                            self.ib.sleep(1)
                except:
                    print("sleeping for 1 seconds <waiting for data>")
                    self.ib.sleep(1)
                   
    def get_delta(self):
        # Calculate Risk Free Rate
        while True:
            try:
                risk_free_rate = creds.risk_free_rate
                break
            except:
                print("exception getting risk free rate . cheak your internet")
                pass

        # Iterate through strikes
            # Sell @ Bid, Buy @ Ask
        
        #option_contracts = self.ib.qualifyContracts(self.option_contract)
        #self.ib.reqMarketDataType(creds.marketdatatype)
        #print(self.option_contract,self.ticker_option)
        #option_contract= Contract(conId = self.option_contract.conId)
        [option_tickers] = self.ib.reqTickers(self.option_contract)
        self.wait_for_data([option_tickers])
        #print("test")
        option_tickers=self.ticker_option
        print(option_tickers.marketPrice(),self.ticker.marketPrice(),option_tickers.last,option_tickers.close)
        
        option_price = self.ticker_option.last
        
        underlying_last_price= self.ticker.marketPrice()
        
        #underlying_last_price=4000
        #option_price=200 #remove when live
        
        print(option_price,underlying_last_price)
        try:
            if(option_price=="nan"):
                print("price is nan")
        except:
            print("exceptions")
        print(self.ticker_option)
        #option_price = 3000
        #underlying_last_price= 3500
        strike=self.option_contract.strike
        days_to_expiration=self.dte + 1
        # Calculate Delta
        calculated_delta = helpers.calculate_delta(
            underlying_last_price,
            strike,
            risk_free_rate,
            days_to_expiration,
            self.put_or_call,
            None,
            option_price,
        )
        print("delta",calculated_delta)
        return calculated_delta
#p1 = CalculateDelta("1","PUT","20221111","C",3)
#print(p1.get_best_strike())