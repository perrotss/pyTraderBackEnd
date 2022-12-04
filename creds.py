port=7496
sl=0.05        # close positions when option price goes below this price

marketdatatype=1

#Naked_Call_Main
Naked_Call_start_hour=9           #time to start
Naked_Call_start_minutes=40       #time to start
Naked_Call_entry_delta=0.1        #entry delta
Naked_Call_dte=0                  #date to expiration
Naked_Call_qty=3
Naked_Call_action="SELL"
Naked_Call_stop_loss_delta=0.45

#Bull_Spread_Main
Bull_Spread_start_hour=12           #time to start
Bull_Spread_start_minutes=40       #time to start
Bull_Spread_entry_delta=-0.16        #entry delta
Bull_Spread_dte=0                  #date to expiration
Bull_Spread_qty=3
Bull_Spread_action="SELL"
Bull_Spread_stop_loss_delta=-0.45
Bull_Spread_below_perc=2
#Bull_Spread2_Main
Bull_Spread2_start_hour=15           #time to start
Bull_Spread2_start_minutes=50       #time to start
Bull_Spread2_entry_delta=-0.1        #entry delta
Bull_Spread2_dte=1                  #date to expiration
Bull_Spread2_qty=3
Bull_Spread2_action="SELL"
Bull_Spread2_stop_loss_delta=-0.50
Bull_Spread2_below_perc=4


#do not change variables below
risk_free_rate=0