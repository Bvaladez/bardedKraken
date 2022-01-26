import logger
import bot
import AssetPairs as AP

class GMM_BOT(bot.Bot):

	def __init__(self, path, pair, sell_levels, buy_levels):
		super(GMM_BOT, self).__init__(path, pair)
		self.mAPI
		self.mPair = pair
		self.mSellLevels = sell_levels
		self.mBuyLevels = buy_levels
		self.mGraph = None
		# Grid consists of buy levels and sell levels
		# TODO: Some API calls should be called in init to eat the free 15 calls we get
	

	def trade(self, base, quote, pair, order_min, asset_pair):
		# Init run
		# This function currently just verifies user keys/secret
		self.initRun()
		orders, balance = self.queryAPI_UserData()
		self.mRunLogger.handlers.pop()
		#### SCOUT/TRADE ####
		# start bot logger
		self.mGMMLogger = logger.setup_logger(pair, pair)
		self.mGMMLogger.info(
			'------------------------- New case --------------------------------')
		# Because of rounding errors balance may need to be rounded down 0.1 worth
		base_balance = float(self.mAPI.get_asset_balance(base))
		quote_balance = float(self.mAPI.get_asset_balance(quote))
		self.mGMMLogger.info(base + ' ' + str(base_balance) + ' ' + quote + ' ' + str(quote_balance))
		# Leverage value: leverage is not used but an option
		lever = 'none'
		# get Ask and bid 
		ask, bid = self.mAPI.get_ask_bid_pair(pair, asset_pair)
		# Create grid of buys and sells 
		sells = []
		best_sell = 0
		i = 0
		best_sell_index = 'No Sell >= ask'

		# finding the nearest sell in our defined grid
		#TODO: Duplicate buys and sells being appended to lists each iter ??????
		for sell in self.mSellLevels:
			# i[1] the level (Price) to sell at.
			if (sell[1] <= bid):
				if (sell[1] > best_sell):
					best_sell = sell[1]
					best_sell_index = i
					continue
				self.mGMMLogger.info(str(sell[1]) + ' sell level <= bid')
			sells.append( [sell[0], sell[1], sell[2], 'sell'] )
			i += 1
		self.mGMMLogger.info('sells ' + str(sells))

		### TODO SEE IF CORRECT SELL IS BEING PULLED
		print("Sells:")
		print(best_sell)
		print(best_sell_index)

		# buys is an array of buy orders data
		best_buy = 0
		i = 0
		best_buy_index = 'No Buy >= ask'
		buys = []
		for buy in self.mBuyLevels:
				# don't cross the book. skip buy levele if buy level >= best ask
				# if someone is offering a lower price than our bid take their ask
			if buy[1] >= ask:
				if (buy[1] > best_buy):
					best_buy = buy[1]
					best_buy_index = i
				self.mGMMLogger.info(str(buy[1]) + ' buy level >= ask')
				# append a buy at their price to change future order
				continue
			# add buy level: [ order size, price, userref, direction of trade ]
			buys.append([buy[0], buy[1], buy[2], 'buy'])
			i += 1
		self.mGMMLogger.info('buys ' + str(buys))

		### TODO SEE IF CORRECT BUY IS BEING PULLED
		print("Buys:")
		print(best_buy)
		print(best_buy_index)

		sells.extend(buys)
		self.mGraph = sells
		print(self.mGraph)
		for price_point in self.mGraph:
			order1, txid1 = self.mAPI.get_order(orders, price_point[2], pair)
			print(order1)
			print(txid1)
			self.mGMMLogger.info('txid1 = ' + str (txid1))

			if price_point[0] >= float(self.mPair['order_min']):
				try:
						# submit following data and place or update order:
						# ( library instance, order info, pair, direction of order,
						# size of order, price, userref, txid of existing order,
						# price precision, leverage, logger instance, oflags )
						# 
						res = self.mAPI.check4trade(order1, pair, price_point[3], price_point[0],
						 						price_point[1], price_point[2], txid1, self.mGMMLogger, 'post')
										
						print(res)
						self.mGMMLogger.info('traded: ' + str(res))
				except Exception as e:
						print('Error occured when ', price_point[3], pair, e)
						self.mGMMLogger.warning('Error occured when ' + price_point[3] + pair + str(e))
				# cancel existing order if new order size is less than minimum
			else:
				res = self.mAPI.check4cancel(order1, txid1)
				print('Not enough funds to ',
							i[3], pair, 'or trade vol too small; canceling', res)
				self.mGMMLogger.info('Not enough funds to ' +
										str(i[3]) + ' ' + pair +
										' or trade vol too small; canceling ' + str(res))
			if res != -1:
					if 'error' in res and res.get('error') != []:
							self.mGMMLogger.warning(pair + ' trading error ' + str(res))
	
		self.mGMMLogger.handlers.pop()
		return

