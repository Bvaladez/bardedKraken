import AssetPairs as AP
# your local path to API keys and logs folder
path_key = 'other/'
path_logs = 'logs/'

# pairs is a list if list that defines tradable pairs and assets:
# [ [ base asset, quote asset, altname from AssetPairs endpoint ], [ ... ] ]
active_pair =  AP.XLMUSD
pairs = [[active_pair['base'], active_pair['quote'], active_pair['pair']]]
order_min = float(active_pair['order_min'])

# sell_levels and buy_levels are lists of lists. It defines:
# [ [ percented of balance to trade, price level, unique userref ], [ ... ] ]
sell_levels = [ [order_min + (.0023*order_min), 0.9998, 101] ]
buy_levels = [ [order_min + (.0025*order_min), 0.9996, 201 ] ]

# Wether or not open orders should be canceled on exit
safeExit = False
