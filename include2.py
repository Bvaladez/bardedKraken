import include as inc
from config import sell_levels, buy_levels

# Trade part


def trade(base, quote, pair0, bal, orders, k, ticker):
    # construct pair from base and quote. USDCUSD is an exception
    pair = base + quote
    if pair == 'USDCZUSD':
        pair = 'USDCUSD'
    # start logger
    logger = inc.setup_logger(pair, pair)
    logger.info(
        '------------------------- New case --------------------------------')
    # assign base and quote balance variables. -0.1 is a trick to get rid
    # of rounding issues and insufficient funds error
    bal_b = float(bal.get(base)) - 0.1
    bal_q = float(bal.get(quote)) - 0.1
    print(base, bal_b)
    print(quote, bal_q)
    logger.info(base + ' ' + str(bal_b) + ' ' + quote + ' ' + str(bal_q))
    # price_cell is a price precision variable
    price_cell = inc.get_price_dec(pair)
    # lever is a leverage value
    lever = 'none'

    # vol_min is a minimum order size. It depends on base currency
    vol_min = inc.get_vol_min(base)
    print(pair)	
    # get best ask/bid from ticker
    ask = float(ticker.get(pair0).get('a')[0])
    bid = float(ticker.get(pair0).get('b')[0])

    # sells is an array of sell orders data
    sells = []
    for i in sell_levels:
        # Don't cross the book. Skip sell levele if sell level <= best bid
				# If someone is offering more money than our sell take their bid
        if i[1] <= bid:
            logger.info(str(i[1]) + ' sell level <= bid')
						# append a sell at their price to change future order
            continue
        # add sell level: [ order size, price, userref, direction of trade ]
        sells.append([i[0] * bal_b, i[1], i[2], 'sell'])
    logger.info('sells ' + str(sells))

    # buys is an array of buy orders data
    buys = []
    for i in buy_levels:
        # don't cross the book. skip buy levele if buy level >= best ask
				# if someone is offering a lower price than our bid take their ask
        if i[1] >= ask:
            logger.info(str(i[1]) + ' buy level >= ask')
						# append a buy at their price to change future order
            continue
        # add buy level: [ order size, price, userref, direction of trade ]
        buys.append([i[0] * bal_q / i[1], i[1], i[2], 'buy'])
    logger.info('buys ' + str(buys))

    # concatenate buys and sells in one 'sells' variable
    for i in buys:
        sells.append(i)

    # -------------- Check for trade @ Kraken
    # iterate through buys and sells level
    for i in sells:
        # get order infor for particular buy/sell level
        order1, txid1 = inc.get_order(orders, i[2], pair0, k)
        print(txid1)
        logger.info('txid1 = ' + str(txid1))
        # check for minimum order size and continue
        if i[0] >= vol_min:
            try:
                # submit following data and place or update order:
                # ( library instance, order info, pair, direction of order,
                # size of order, price, userref, txid of existing order,
                # price precision, leverage, logger instance, oflags )
                res = inc.check4trade(
                    k, order1, pair, i[3], i[0], i[1], i[2], txid1,
                    price_cell, lever, logger, 'post')
										
                print(res)
                logger.info('traded: ' + str(res))
            except Exception as e:
                print('Error occured when ', i[3], pair0, e)
                logger.warning('Error occured when ' + i[3] + pair0 + str(e))
        # cancel existing order if new order size is less than minimum
        else:
            res = inc.check4cancel(k, order1, txid1)
            print('Not enough funds to ',
                  i[3], pair0, 'or trade vol too small; canceling', res)
            logger.info('Not enough funds to ' +
                        str(i[3]) + ' ' + pair0 +
                        ' or trade vol too small; canceling ' + str(res))
        if res != -1:
            if 'error' in res and res.get('error') != []:
                logger.warning(pair + ' trading error ' + str(res))
    logger.handlers.pop()
