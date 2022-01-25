import include as inc
import AssetPairs as AP
import bot

class GMM_BOT(bot.Bot):

	def __init__(self, path, pair, sell_levels, buy_levels):
		super(GMM_BOT, self).__init__(path, pair)
		self.mAPI
		self.mPair = pair
		self.mSellLevels = sell_levels
		self.mBuyLevels = buy_levels
		# Grid consists of buy levels and sell levels
		self.mGrid = self.mSellLevels.extend(self.mBuyLevels)
		# TODO: Some API calls should be called in init to eat the free 15 calls we get
	

	def trade(self, base, quote, pair, order_min, asset_pair):
		# INIT RUN
		self.initRun()
		orders, balance = self.queryAPI_UserData()
		self.mRunLogger.handlers.pop()
		# SCOUT/TRADE
		# start bot logger
		self.mGMMLogger = inc.setup_logger(pair, pair)
		self.mGMMLogger.info(
			'------------------------- New case --------------------------------')
		# Because of rounding errors balance may need to be rounded down 0.1 worth
		base_balance = float(self.mAPI.get_asset_balance(base))
		quote_balance = float(self.mAPI.get_asset_balance(quote))

		print('         Current Balance       ')
		print(base, base_balance, '|', quote, quote_balance)
		self.mGMMLogger.info(base + ' ' + str(base_balance) + ' ' + quote + ' ' + str(quote_balance))

		# Leverage value
		lever = 'none'

		# get minumum trade

		# get Ask and bid 
		## API cant see inc but inc can see API 
		ask, bid = inc.get_ask_bid_pair(self.mAPI, pair, asset_pair)

		# Create grid of buys and sells 
		sells = []
		best_sell = 0
		i = 0
		best_sell_index = 'No Sell >= ask'
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

		print("Buys:")
		print(best_buy)
		print(best_buy_index)




		# For every buy and sell if their price is the same 
		# as the current price execute order

		
 

		self.mGMMLogger.handlers.pop()
		return

