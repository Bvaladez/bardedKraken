from logging import Logger, log
import krakenex
import include as inc
import include2 as inc2
import time

### OUT OF PHASE PAIRS ###

# find closely correlated graphs between tickers
# find the shifting coeficient from base to quote
# determine buys off significant positive shifts in base
# determine sells off significatn negative shfits in base

#########
#IDEAL WORLD SIT:##
######### 
''' find function
of base graph, apply
translation function to
graph know where quote 
is trending '''
#########


class Bot:

	def __init__(self, path, pairs):
		self.mKeyPath = path
		self.mPairs = pairs
		self.mAPI = krakenex.API()
		self.mRunLogger = inc.setup_logger('Bot', 'Bot')

	def handleSafeExit(self):
		if ( self.mAPI.get_open_orders() != {} ):
			count = self.mAPI.cancel_open_orders()
			self.mRunLogger.info(count + " open orders were attempted to cancel on exit.")
		return

	# Verifies key, Returns an instance of kraken API and local logger
	def initRun(self):
		self.mAPI.load_key(self.mKeyPath + 'k0.key')
		return

	# Return orders, balances (formatted for trade call)
	def queryAPI_UserData(self):

		allOrders = self.mAPI.query_private('OpenOrders')
		allBalances = self.mAPI.query_private('Balance')

		# sanity check: checking OpenOrders result and retry if needed
		if allOrders.get('error') == []:
				orders = allOrders.get('result').get('open')
		else:
				self.mRunLogger.warning('Order error ' + str(allOrders.get('error')))
				orders = self.mAPI.query_private('OpenOrders').get('result').get('open')
		# sanity check: checking Balance result and retry if needed
		if allBalances.get('error') == []:
				balance = allBalances.get('result')
		else:
				self.mRunLogger.warning('Balance error ' + str(allBalances.get('error')))
				balance = self.mAPI.query_private('Balance').get('result')
		return orders, balance
