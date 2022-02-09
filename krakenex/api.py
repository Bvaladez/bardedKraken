# This file is part of krakenex.
#
# krakenex is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# krakenex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public LICENSE along with krakenex. If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> and
# <http://www.gnu.org/licenses/gpl-3.0.txt>.

# This API gives 15 API counters 
# ledger/trade calls increase counter by 2 other API calls increase by 1
# The decay rate for our level is -0.33/sec

# API order counter maxes at 60 open orders per pair
# API ratecount maxes at 60 add Order is +1 cancel order <5sec +8 <10sec +6 <15sec +5 .... >300s +0

"""Kraken.com cryptocurrency Exchange API."""

from logging import raiseExceptions
import requests

# private query nonce
import time

# private query signing
import urllib.parse
import hashlib
import hmac
import base64

from . import version

class API(object):
	""" Maintains a single session between this machine and Kraken.

	Specifying a key/secret pair is optional. If not specified, private
	queries will not be possible.

	The :py:attr:`session` attribute is a :py:class:`requests.Session`
	object. Customise networking options by manipulating it.

	Query responses, as received by :py:mod:`requests`, are retained
	as attribute :py:attr:`response` of this object. It is overwritten
	on each query.

	.. note::
		 No query rate limiting is performed.

	"""
	def __init__(self, key='', secret=''):
			""" Create an object with authentication information.

			:param key: (optional) key identifier for queries to the API
			:type key: str
			:param secret: (optional) actual private key used to sign messages
			:type secret: str
			:returns: None

			"""
			self.key = key
			self.secret = secret
			self.uri = 'https://api.kraken.com'
			self.apiversion = '0'
			self.session = requests.Session()
			self.session.headers.update({
					'User-Agent': 'krakenex/' + version.__version__ + ' (+' + version.__url__ + ')'
			})
			self.response = None
			self._json_options = {}
			return

	#######
	# These API call implementations need to be TESTED


	def get_open_orders(self):
		orders = self.query_private('OpenOrders').get('result').get('open')
		return orders

	def cancel_open_orders(self):
		closed_orders = self.query_private('CancelAll').get('result').get('count')
		return closed_orders

	def get_spread_data(self, pair):
		spread = self.query_public('Spread', { 'pair':pair } )
		return spread

	def get_asset_balance(self, asset):
		balance_resp = self.query_private('Balance')
		balance_result = balance_resp.get('result')
		asset_balance = balance_result.get(asset)
		if balance_result != None:
			if asset_balance != None:
				return asset_balance
			# No balance of current currency
			else:
				return 0
		else:
			raiseExceptions("API call to Balance->Results Failed")


	def get_trade_volume(self, pair):
		volume = self.query_private('TradeVolume', { 'pair':pair} ).get('result')
		return volume

	#
	####### 

	# Return pairs string for ticker call
	def get_ticker_pairs(self, pairs):
		if ( type(pairs) == 'list'):
			res = pairs[0][2]
			n = len(pairs)
			for i in range(1, n):
					res = res + ',' + pairs[i][2]
			return res
		elif (type(pairs) is dict):
			return pairs['pair']

	# here we use pair and userref to distinguish between orders
	# return txid and order information
	def get_order(self, opened_orders, ref, pair):
			order1 = -1
			open2 = -1
			for open1 in opened_orders:
					if opened_orders.get(open1).get('userref') == ref and \
									opened_orders.get(open1).get('descr').get('pair') == pair:
							if order1 != -1:
									close_k = self.query_private('CancelOrder', {'txid': open1})
									print("canceled", open1, close_k)
									time.sleep(1)
									continue
							order1 = opened_orders.get(open1)
							open2 = open1
			return order1, open2

	# Places or updates orders
	def check4trade(self, order, pair, buyorsell, vol, price, ref, txid, logger, post):
		trade = -1
		'''
		If order does not currently exist, place it.
		Order size and price is truncated to meet 
		precesion requirements
		'''
		if order == -1:
				trade = self.query_private('AddOrder',  {'pair': pair, 'type': buyorsell, 'ordertype': 'limit', 'volume': str(
						'%.8f' % vol), 'price': str(price), 'userref': ref, 'oflags': post})
																			#(price_cell % price)
		else:
				# if an order currently exists at this price level, we check if it has
				# to be updated. We use 0.02% price tolerance and 2% size tolerance
				if abs(1 - float(order.get('descr').get('price')) / float(price)) > 0.0002 or abs(1 - vol / float(order.get('vol'))) > 0.02:
						close_k = self.query_private('CancelOrder', {'txid': txid})
						logger.info('close result ' + str(close_k))
						close_res = -1
						try:
								close_res = int(close_k.get('result').get('count'))
						except:
								pass
						if close_res == 1:
								trade = self.query_private('AddOrder',  {'pair': pair, 'type': buyorsell, 'ordertype': 'limit', 'volume': str(
										'%.8f' % vol), 'price': str(price), 'userref': ref, 'oflags': post})
				else:
						print('Order not changed', txid)
						logger.info('Order not changed ' + str(txid))
		return trade

	# Only cancel if order exist (!=-1)
	def check4cancel(self, order, txid):
		close_k = -1
		if order != -1:
			close_k = self.query_private('CancelOrder', {'txid': txid})
		return close_k

	# Return price precision
	# %.1f = 1 decimal
	def get_price_dec(self, pair):
		res = 1  # USD, EUR to XBT is included here
		if pair in ['USDTZUSD', 'USDCUSD']:
				res = 4
		return '%.' + str(res) + 'f'

	# Get ask bid as a tuple
	def get_ask_bid_pair(self, pair, asset_pair):
		ticker_pair = self.get_ticker_pairs(asset_pair)
		ticker = self.query_public('Ticker', {'pair': ticker_pair})
		ask = float(ticker.get('result').get(pair).get('a')[0])
		bid = float(ticker.get('result').get(pair).get('b')[0])
		return ask, bid

	# Get ask
	def get_ask_pair(self, pair):
		ticker = self.query_public('Ticker', {'pair': pair})
		ask = ticker.get(pair).get('a')[0]
		return ask

	# Get Bid
	def get_bid_pair(self, pair):
		ticker = self.query_public('Ticker', {'pair': pair})

		bid = ticker.get(pair).get('b')[0]
		return bid


	################################################################################# 
	########################     BASE KRAKEN API CALLS     ##########################
	################################################################################# 

	def json_options(self, **kwargs):
		""" Set keyword arguments to be passed to JSON deserialization.

		:param kwargs: passed to :py:meth:`requests.Response.json`
		:returns: this instance for chaining

		"""
		self._json_options = kwargs
		return self

	def close(self):
		""" Close this session.

		:returns: None

		"""
		self.session.close()
		return

	def load_key(self, path):
		""" Load key and secret from file.

		Expected file format is key and secret on separate lines.

		:param path: path to keyfile
		:type path: str
		:returns: None

		"""
		with open(path, 'r') as f:
				self.key = f.readline().strip()
				self.secret = f.readline().strip()
		return

	def _query(self, urlpath, data, headers=None, timeout=None):
		""" Low-level query handling.

		.. note::
			 Use :py:meth:`query_private` or :py:meth:`query_public`
			 unless you have a good reason not to.

		:param urlpath: API URL path sans host
		:type urlpath: str
		:param data: API request parameters
		:type data: dict
		:param headers: (optional) HTTPS headers
		:type headers: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
										will be thrown after ``timeout`` seconds if a response
										has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object
		:raises: :py:exc:`requests.HTTPError`: if response status not successful

		"""
		if data is None:
				data = {}
		if headers is None:
				headers = {}

		url = self.uri + urlpath

		self.response = self.session.post(url, data = data, headers = headers,
																			timeout = timeout)

		if self.response.status_code not in (200, 201, 202):
				self.response.raise_for_status()

		return self.response.json(**self._json_options)


	def query_public(self, method, data=None, timeout=None):
		""" Performs an API query that does not require a valid key/secret pair.

		:param method: API method name
		:type method: str
		:param data: (optional) API request parameters
		:type data: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
										will be thrown after ``timeout`` seconds if a response
										has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object

		"""
		if data is None:
				data = {}

		urlpath = '/' + self.apiversion + '/public/' + method

		return self._query(urlpath, data, timeout = timeout)

	def query_private(self, method, data=None, timeout=None):
		""" Performs an API query that requires a valid key/secret pair.

		:param method: API method name
		:type method: str
		:param data: (optional) API request parameters
		:type data: dict
		:param timeout: (optional) if not ``None``, a :py:exc:`requests.HTTPError`
										will be thrown after ``timeout`` seconds if a response
										has not been received
		:type timeout: int or float
		:returns: :py:meth:`requests.Response.json`-deserialised Python object

		"""
		if data is None:
				data = {}

		if not self.key or not self.secret:
				raise Exception('Either key or secret is not set! (Use `load_key()`.')

		data['nonce'] = self._nonce()

		urlpath = '/' + self.apiversion + '/private/' + method

		headers = {
				'API-Key': self.key,
				'API-Sign': self._sign(data, urlpath)
		}

		return self._query(urlpath, data, headers, timeout = timeout)

	def _nonce(self):
		""" Nonce counter.

		:returns: an always-increasing unsigned integer (up to 64 bits wide)

		"""
		return int(1000*time.time())

	def _sign(self, data, urlpath):
		""" Sign request data according to Kraken's scheme.

		:param data: API request parameters
		:type data: dict
		:param urlpath: API URL path sans host
		:type urlpath: str
		:returns: signature digest
		"""
		postdata = urllib.parse.urlencode(data)

		# Unicode-objects must be encoded before hashing
		encoded = (str(data['nonce']) + postdata).encode()
		message = urlpath.encode() + hashlib.sha256(encoded).digest()

		signature = hmac.new(base64.b64decode(self.secret),
												 message, hashlib.sha512)
		sigdigest = base64.b64encode(signature.digest())

		return sigdigest.decode()
