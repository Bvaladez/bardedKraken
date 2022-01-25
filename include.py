
import time

# ALL FUNCTION IN FILE HAVE MOVED TO KRAKENEX/API
# REMOVE AFTER REFACTOR


# -------------- Return pairs string for ticker call
def get_ticker_pairs(pairs):
	if ( type(pairs) == 'list'):
		res = pairs[0][2]
		n = len(pairs)
		for i in range(1, n):
				res = res + ',' + pairs[i][2]
		return res
	elif (type(pairs) is dict):
		return pairs['pair']


# -------------- Order select

# here we use pair and userref to distinguish between orders
# return txid and order information
def get_order(opened, ref, pair0, k):
		order1 = -1
		open2 = -1
		for open1 in opened:
				if opened.get(open1).get('userref') == ref and \
						opened.get(open1).get('descr').get('pair') == pair0:
						if order1 != -1:
								close_k = k.query_private('CancelOrder', {'txid': open1})
								print("canceled", open1, close_k)
								time.sleep(1)
								continue
						order1 = opened.get(open1)
						open2 = open1
		return order1, open2

# -------------- Check for trade
# this function places or updates orders


def check4trade(k, order, pair, buyorsell, vol, price, ref, txid, price_cell,
								lever, logger, post):
		trade = -1
		# if order does not currently exist, we place it. Order size and price is
		# truncated to meet precesion requirements
		if order == -1:
				trade = k.query_private('AddOrder',  {'pair': pair, 'type': buyorsell, 'ordertype': 'limit', 'volume': str(
						'%.8f' % vol), 'price': str(price), 'userref': ref, 'oflags': post})
																			#(price_cell % price)
		else:
				# if an order currently exists at this price level, we check if it has
				# to be updated. We use 0.02% price tolerance and 2% size tolerance
				if abs(1 - float(order.get('descr').get('price')) / float(price)) > 0.0002 or abs(1 - vol / float(order.get('vol'))) > 0.02:
						close_k = k.query_private('CancelOrder', {'txid': txid})
						logger.info('close result ' + str(close_k))
						close_res = -1
						try:
								close_res = int(close_k.get('result').get('count'))
						except:
								pass
						if close_res == 1:
								trade = k.query_private('AddOrder',  {'pair': pair, 'type': buyorsell, 'ordertype': 'limit', 'volume': str(
										'%.8f' % vol), 'price': str(price), 'userref': ref, 'oflags': post})
				else:
						print('Order not changed', txid)
						logger.info('Order not changed ' + str(txid))
		return trade

# --------------- Only cancel if order exist (!=-1)


def check4cancel(k, order, txid):
		close_k = -1
		if order != -1:
				close_k = k.query_private('CancelOrder', {'txid': txid})
		return close_k

# --------------- Return Minimum Volume depending on asset


def get_vol_min(asset):
		tr = {'USDT': 5, 'USDC': 5}
		return tr[asset]


# ---------------- Return price precision
# %.1f = 1 decimal

def get_price_dec(pair):
		res = 1  # USD, EUR to XBT is included here
		if pair in ['USDTZUSD', 'USDCUSD']:
				res = 4
		return '%.' + str(res) + 'f'

#------------------ get ask bid as a tuple
def get_ask_bid_pair(API, pair, asset_pair):
	ticker_pair = get_ticker_pairs(asset_pair)
	ticker = API.query_public('Ticker', {'pair': ticker_pair})
	print(ticker)
	ask = float(ticker.get('result').get(pair).get('a')[0])
	bid = float(ticker.get('result').get(pair).get('b')[0])
	return ask, bid

#------------------ get ask bid as a tuple
def get_ask_pair(API, pair):
	ticker = API.query_public('Ticker', {'pair': pair})
	ask = ticker.get(pair).get('a')[0]
	return ask

def get_bid_pair(API, pair):
	ticker = API.query_public('Ticker', {'pair': pair})
	bid = ticker.get(pair).get('b')[0]
	return bid
