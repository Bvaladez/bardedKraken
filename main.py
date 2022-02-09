#! /usr/bin/env python3

import config
import time

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

def main():
	while True:
		bot = None
		try:
			bot =	gmmBot.GMM_BOT(path, active_pair, sell_levels, buy_levels)
			bot.trade(active_pair['base'], active_pair['quote'], active_pair['pair'], active_pair['order_min'], active_pair)
				# Decay time is -.33/sec Trades/cancels add marks
			time.sleep(3.2)
		except Exception as e:
			print('main.py', 'exeption thrown on bot initializing or trade function')
			print(e)
		finally:
			# SAFEEXIT determines if open orders are before closing connection to API
			if(SAFEEXIT and bot != None):
			# TODO: Verify that this function has to be succesful or notification is given
				bot.handleSafeExit()
		return 0

def test():
	while True:
		bot = None
		#try:
		bot =	gmmBot.GMM_BOT(path, active_pair, sell_levels, buy_levels)
		bot.trade(active_pair['base'], active_pair['quote'], active_pair['pair'], active_pair['order_min'], active_pair)
			# Decay time is -.33/sec Trades/cancels add marks
		time.sleep(3.2)
		#except Exception as e:
		#	print('main.py', 'exeption thrown on bot initializing or trade function')
		#	print(e)
		#finally:
			# SAFEEXIT determines if open orders are before closing connection to API
		#	if(SAFEEXIT and bot != None):
		#		# TODO: Verify that this function has to be succesful or notification is given
		#		bot.handleSafeExit()
	return 0
if __name__ == "__main__":
		test()
		#main()