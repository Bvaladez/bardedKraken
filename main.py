#! /usr/bin/env python3

# These three includes are only used in our run2 version of running
# REMOVE AFTER REFACTOR
import krakenex
import include as inc
import include2 as inc2

import config
import time

import bot
import grid_market_maker_BOT as gmmBot

from config import sell_levels, buy_levels


# loading path to API keys
path = config.path_key
# getting bot trading pairs from config file
allPairs = config.pairs
# Active pair used for GMM bot
active_pair = config.active_pair
# get safe close option
SAFEEXIT = config.safeExit



def run2(pairs):
		# starting logger
		logger_run2 = inc.setup_logger('run2', 'run2')
		# loading Kraken library and key
		k = krakenex.API()
		k.load_key(path + 'k0.key')
		# get Open Orders from API
		orders_all = k.query_private('OpenOrders')
		# get Balance from API
		bal_all = k.query_private('Balance')
		# constructing pairs as a string to input into Ticker call
		pairs_t = inc.get_ticker_pairs(allPairs)
		# get prices with Ticker call
		ticker = k.query_public('Ticker', {'pair': pairs_t})
		#print(ticker)

		# sanity check: checking OpenOrders result and retry if needed
		if orders_all.get('error') == []:
				orders = orders_all.get('result').get('open')
		else:
				logger_run2.warning('Order error ' + str(orders_all.get('error')))
				orders = k.query_private('OpenOrders').get('result').get('open')

				# sanity check: checking Balance result and retry if needed
		if bal_all.get('error') == []:
				bal = bal_all.get('result')
		else:
				logger_run2.warning('Balance error ' + str(bal_all.get('error')))
				bal = k.query_private('Balance').get('result')

		# Start trading algorithm for all pairs
		for i in range(len(pairs)):
				inc2.trade(pairs[i][0], pairs[i][1], pairs[i]
									 [2], bal, orders, k, ticker['result'])
		# Stop the logger
		logger_run2.handlers.pop()


def run():
		while True:
				try:
						run2(allPairs)
				except Exception as e:
					print(e)
				time.sleep(3)
		return 

def main():
	while True:
		bot = None
		try:
			bot =	gmmBot.GMM_BOT(path, active_pair, sell_levels, buy_levels)
			bot.trade(active_pair['base'], active_pair['quote'], active_pair['pair'], active_pair['order_min'], active_pair)
			# Decay time is -.33/sec Trades/cancels add marks
			time.sleep(.5)
		except Exception as e:
			print('main.py', 'exeption thrown on bot initializing or trade function')
			print(e)
		finally:
			# SAFEEXIT determines if open orders are before closing connection to API
			if(SAFEEXIT and bot != None):
				# TODO: Verify that this function has to be succesful or notification is given
				bot.handleSafeExit()
	return

if __name__ == "__main__":
		#run()
		main()