import krakenex
import logger
import user

class Bot:

	def __init__(self, path, pairs):
		self.mKeyPath = path
		self.mPairs = pairs
		self.mAPI = krakenex.API()
		self.ValidateApiKey()
		self.mRunLogger = logger.setup_logger('Bot', 'Bot')

	def handleSafeExit(self):
		if ( self.mAPI.get_open_orders() != {} ):
			count = self.mAPI.cancel_open_orders()
			self.mRunLogger.info(count + " open orders were attempted to cancel on exit.")
		return

	# Verifies key, Returns an instance of kraken API and local logger
	def ValidateApiKey(self):
		self.mAPI.load_key(self.mKeyPath + 'k0.key')
		return

	def queryAPI_allOrders(self):
		allOrders = self.mAPI.query_private('OpenOrders')
		# sanity check: checking OpenOrders result and retry if needed
		if allOrders.get('error') == []:
				orders = allOrders.get('result').get('open')
		else:
				self.mRunLogger.warning('Order error ' + str(allOrders.get('error')))
				orders = self.mAPI.query_private('OpenOrders').get('result').get('open')

		return orders
	
	# Return orders, balances (formatted for trade call)
	def queryAPI_balance(self):

		allBalances = self.mAPI.query_private('Balance')

			# sanity check: checking Balance result and retry if needed
		if allBalances.get('error') == []:
				balance = allBalances.get('result')
		else:
				self.mRunLogger.warning('Balance error ' + str(allBalances.get('error')))
				balance = self.mAPI.query_private('Balance').get('result')
		return balance
