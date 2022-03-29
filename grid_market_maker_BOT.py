import logger
import bot
import AssetPairs as AP

class GMM_BOT(bot.Bot):

	def __init__(self, path, pair):
		super(GMM_BOT, self).__init__(path, pair)
		self.mAPI
		self.mPair: dict[str, str] = pair
		self.mBase = pair['base']
		self.mQuote = pair['quote']
		self.mPairName = self.mBase + self.mQuote
		self.mPairOrderMin = pair['order_min']
		self.mTradeVolume = self.mPairOrderMin
		self.mPairFeePercent: float = 0.16
		self.mSpread: float = float(bot.user.getUserInput("Spread? (Warning given if spread is not profitable) "))
		self.mBuyMin: float = float(bot.user.getUserInput("Minimum buy? "))
		self.mBuyMax: float = float(bot.user.getUserInput("Maximum buy? "))
		self.mSellMin: float = float(bot.user.getUserInput("Minimum sell? "))
		self.mSellMax: float = float(bot.user.getUserInput("Maximum sell? "))
		self.mOrderGrid = self.createOrderGrid(self.mSpread, self.mBuyMin, self.mBuyMax, self.mSellMin, self.mSellMax )
		self.baseBalance = float(self.mAPI.get_asset_balance(pair['base']))
		self.quoteBalance = float(self.mAPI.get_asset_balance(pair['quote']))

	def createOrderGrid(self, spread: float, buyMin: float, buyMax: float, sellMin: float, sellMax: float):
		# The trade volume needs to be multiplied by the price to check if in range for profitablility
		if (spread - (float(self.mTradeVolume) * self.mPairFeePercent )) <= 0:
			print("Chosen spread will not be profitable on trades")
		buyRef = 1
		sellRef = 10000
		buyPoint = buyMin
		buys = []
		while ( buyPoint < buyMax ):
			buys.append({'volume': self.mPairOrderMin, 'price' : buyPoint, 'ref' : buyRef, 'buy_sell' : "buy"})
			buyPoint += spread
			buyRef += 1
		sellPoint =  sellMin
		sells = []
		while (sellPoint < sellMax):
			buys.append({'volume': self.mPairOrderMin, 'price' : sellPoint, 'ref' : sellRef, 'buy_sell' : "sell"})
			sellPoint += spread
			sellRef += 1
		orderGrid = sells.extend(buys)
		return orderGrid


	def trade(self, base, quote, pair, order_min):
		orders = self.queryAPI_allOrders()

		#### SCOUT/TRADE ####
		# start bot logger
		self.mGMMLogger = logger.setup_logger(self.mPairName, self.mPairName)
		self.mGMMLogger.info(
			'------------------------- New case --------------------------------')
		# Because of rounding errors balance may need to be rounded down 0.1 worth
		self.mGMMLogger.info(base + ' ' + str(self.baseBalance) + ' ' + quote + ' ' + str(self.quoteBalance))

		### TODO SEE IF CORRECT BUY IS BEING PULLED
		for orderToPlace in self.mOrderGrid:
			order1, txid1 = self.mAPI.get_order(orders, orderToPlace['price'], pair)
			self.mGMMLogger.info('txid1 = ' + str (txid1))
			if orderToPlace['volume'] >= float(self.mPair['order_min']):
				try:
						# submit following data and place or update order:
						# ( library instance, order info, pair, direction of order,
						# size of order, price, userref, txid of existing order,
						# price precision, leverage, logger instance, oflags )
						# 
						res = self.mAPI.check4trade(order1, pair, orderToPlace['buy_sell'], orderToPlace['volume'],
						 						orderToPlace['price'], orderToPlace['ref'], txid1, self.mGMMLogger, 'post')
										
						self.mGMMLogger.info('traded: ' + str(res))
				except Exception as e:
						print('Error occured when ', orderToPlace['buy_sell'], pair, e)
						self.mGMMLogger.warning('Error occured when ' + orderToPlace['buy_sell'] + pair + str(e))
				# cancel existing order if new order size is less than minimum
			else:
				res = self.mAPI.check4cancel(order1, txid1)
				print('Not enough funds to ', orderToPlace['buy_sell'], pair, 'or trade vol too small; canceling', res)
				self.mGMMLogger.info('Not enough funds to ' +
										str(orderToPlace['buy_sell']) + ' ' + pair +
										' or trade vol too small; canceling ' + str(res))
			if res != -1:
					if 'error' in res and res.get('error') != []:
							self.mGMMLogger.warning(pair + ' trading error ' + str(res))
	
		self.mGMMLogger.handlers.pop()
		return

