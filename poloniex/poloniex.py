import requests
import json
import time
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
import hmac,hashlib

PUBLIC_REQUESTS = {'returnTicker', 'return24hVolume', 'returnOrderBook', 'returnMarketTradeHistory', 'returnCurrencies'}

BASE_URL = 'https://poloniex.com/'


class Poloniex:
    def __init__(self, APIKey='', Secret=''):
        self.APIKey = str(APIKey) if APIKey is not None else ''
        self.Secret = str(Secret) if Secret is not None else ''

    def load_key(self, path):
        """
        Load key and secret from file.

        :param path: path to keyfile
        :type path: str
        """
        with open(path, 'r') as secrets_file:
            secrets = json.load(secrets_file)
            secrets_file.close()
        self.APIKey = secrets['key']
        self.Secret = secrets['secret']

    def api_query(self, method, options={}):

        options['command'] = method

        if method in PUBLIC_REQUESTS:
            # 'returnTradeHistory' in both public and trade API
            if (method == 'returnMarketTradeHistory'):
                options['command'] = 'returnTradeHistory'
            request_url = BASE_URL + 'public?'
            post_data   = urlencode(options)
            res         = requests.post(request_url + post_data)

        else:
            options['nonce'] = int(time.time()*1000)
            request_url      = BASE_URL + 'tradingApi?'
            post_data        = urlencode(options)
            sign             = hmac.new(self.Secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()
            headers          = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Sign'        : sign,
                'Key'         : self.APIKey
            }
            res = requests.post(request_url, data = post_data, headers = headers)

        return res.json()


    ## Public API methods

    def returnTicker(self):
        """
        Returns the ticker for all markets.

        :rtype: dict
        """
        return self.api_query("returnTicker")

    def return24hVolume(self):
        """
        Returns the 24-hour volume for all markets, plus totals for primary currencies.

        :rtype: dict
        """
        return self.api_query("return24hVolume")

    def returnOrderBook(self, currencyPair):
        """
        Returns the order book for a given market.

        :return:
            asks        list of asks
            bids        list of bids
            isFrozen    indicator specifying whether the market is frozen
            seq         sequence number for use with the Push API
        :rtype: dict
        """
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})

    def returnMarketTradeHistory(self, currencyPair, start, end):
        """
        Returns the past 200 trades for a given market, or up to 50,000 trades between a range specified.

        :param currencyPair
        :type currencyPair: str

        :param start: optional time interval start
        :type start: UNIX timestamp

        :param start: optional time interval end
        :type start: UNIX timestamp

        :rtype: list
        """
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair, 'start': start, 'end': end})

    def returnCurrencies(self):
        """
        Returns information about currencies.

        :rtype: dict
        """
        return self.api_query('returnCurrencies')


    ## TradingAPI methods

    def returnBalances(self):
        """
        Returns all account balances.

        :return: {"BTC":"0.59098578","LTC":"3.31117268", ... }
        :rtype : dict
        """
        return self.api_query('returnBalances')

    def returnCompleteBalances(self, account):
        """
        Returns all account balances (on exchange account), including available, balance on orders, estimated BTC value of balances.

        :param account: 'all' to include margin and lending accounts
        :type account: str

        :return:
        :rtype: dict
        """
        return self.api_query('returnCompleteBalances', {'account': account})

    def returnOpenOrders(self, currencyPair):
        """
        Returns open orders for a given market.

        :param currencyPair:
        :type currencyPair: str

        :return:
            orderNumber
            type          sell or buy
            rate          sell/buy price
            Amount        order quantity
            total         Total value of order (price * quantity)
        :rtype:
        """
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})

    def returnDepositAddress(self):
        """
        Returns all account deposit addresses.

        :rtype: dict
        """
        return self.api_query('returnDepositAddress')

    def generateNewAddress(self, currency):
        """
        Generates a new deposit address for the currency specified.

        :param currency
        :type currency: str

        :return:
            success     0 or 1
            response    the deposit address
        :rtype: dict
        """
        return self.api_query('generateNewAddress', {'currency': currency})

    def returnDepositsWithdrawals(self, start, end):
        """
        Returns your deposit and withdrawal history within a range, specified by the "start" and "end".

        :param start
        :type start: UNIX timestamp
        :param end
        :type end: UNIX timestamp

        :return:
            deposits     list of deposits:
                currency
                address
                amount
                confirmattions
                txid
                timestamp
                status
            withdrawals   list of withdrawals:
                withdrawalNumber
                currency
                address
                amount
                timestamp
                status
        :rtype: dict
        """
        return self.api_query('returnDepositsWithdrawals', {'start': start, 'end': end})

    def returnOpenOrders(self, currencyPair):
        """
        Returns open orders for a given market.

        :param currencyPair: 'all' or e.g. 'BTC_ZEC'
        :type currencyPair: str

        :return: orders
        :rtype: list
        """
        return self.api_query('returnOpenOrders', {'currencyPair': currencyPair})


    def returnTradeHistory(self, currencyPair):
        """
        Returns account trade history for a given market.

        :param currencyPair : 'all' or the currency pair (e.g. 'BTC_XCP')
        :type currencyPair  : str
        :return:
            date          Date in the form: "2014-02-19 03:44:59"
            rate          buy/sell price
            amount        order quantity
            total         Total value of order (price * quantity)
            type          sell or buy
        :rtype: list (or for all markets, dict)
        """
        return self.api_query('returnTradeHistory', {"currencyPair": currencyPair})

    def returnOrderTrades(self, orderNumber):
        """
        Returns all trades involving a given order.

        :param orderNumber
        :type orderNumber:

        :return: list of trades
        :rtype: list
        """
        return self.api_query(self, {'orderNumber': orderNumber})

    def buy(self, currencyPair, rate, amount):
        """
        Places a buy order in a given market.
        If successful, the method will return the order number.

        :param currencyPair: The curreny pair
        :type currencyPair: str
        :param rate: buy price
        :type rate:
        :param amount: buy amount
        :type amount:

        :return:
            orderNumber : The order number
        :rtype:
        """
        return self.api_query('buy', {"currencyPair": currencyPair, "rate": rate, "amount": amount})

    def sell(self, currencyPair, rate, amount):
        """
        Places a sell order in a given market.
        If successful, the method will return the order number.

        :param currencyPair: The curreny pair
        :type currencyPair: str
        :param rate: sell price
        :type rate:
        :param amount: sell amount
        :type amount:

        :return:
            orderNumber : The order number
        :rtype:
        """
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    def cancelOrder(self, currencyPair, orderNumber):
        """
        Cancels an order placed in a given market.

        :param currencyPair:  The curreny pair
        :orderNumber:   The order number to cancel

        :return:
            succes: 1 or 0
        :rtype: int
        """
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    def moveOrder(self, orderNumber, rate, amount):
        """
        Cancels an order and places a new one of the same type in a single atomic transaction.

         "postOnly" or "immediateOrCancel" may be specified for exchange orders, but will have no effect on margin orders.

        :param orderNumber: order to be changed
        :type orderNumber: str

        :param rate: order price
        :type rate:

        :param amount: optionally specify if the amount should be changed
        :type amount:

        :return:
            success             0 or 1
            orderNumber         str
            resultingTrades     dict

        :rtype: dict
        """
        return self.api_query('moveOrder', {'orderNumber': orderNumber})

    def withdraw(self, currency, amount, address):
        """
        Places a withdrawal for a given currency, with no email confirmation.
        In order to use this method, the withdrawal privilege must be enabled for your API key.

        Inputs:
        :param currency: The currency to withdraw
        :type currency:
        :param amount: The amount to withdraw
        :type amount:
        :param address: The withdrawal address
        :type address:

        :return:
            response: Text message about the withdrawal
        :rtype: dict
        """
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})

    def returnFeeInfo(self):
        """
        If you are enrolled in the maker-taker fee schedule, returns your current trading fees and trailing 30-day volume in BTC.

        :return:
            makerFee
            takerFee
            thirtyDayVolume
            nextTier
        :rtype: dict
        """
        return self.api_query('returnFeeInfo')

    def transferBalance(self, currency, amount, fromAccount, toAccount):
        """
        Returns current tradable balances for each currency in each market for which margin trading is enabled.

        :param currency
        :type currency: str

        :param amount: amount to transfer
        :type amount:

        :param fromAccount
        :type fromAccount: str

        :param toAccount
        :type toAccount: str

        :return:
            success     0 or 1
            message     msg about the transfer
        :rtype: dict
        """
        return self.api_query('transferBalance', {'currency': currency, 'amount': amount, 'fromAccount': fromAccount, 'toAccount': toAccount})

    ## Margin Trading methods

    def returnTradeBalances(self):
        """
        Returns current tradable balances for each currency in each market for which margin trading is enabled.

        :return:
        :rtype: dict
        """
        return self.api_query('returnTradableBalances')

    def returnMarginAccountSummary(self):
        """
        Returns a summary of your entire margin account.

        :return:
            totalValue
            pl
            lendingFees
            netValue
            totalBorrowedValue
            currentMargin
        :rtype: dict
        """
        return self.api_query('returnMarginAccountSummary')

    def marginBuy(self, currencyPair, rate, amount, lendingRate):
        """
        Places a margin buy order in a given market.
        Required POST parameters are "currencyPair", "rate", and "amount".
        You may optionally specify a maximum lending rate using the "lendingRate" parameter.
        If successful, the method will return the order number and any trades immediately resulting from your order.
        """
        return self.api_query('marginBuy', {'currencyPair': currencyPair, 'rate': rate, 'amount': amount, 'lendingRate': lendingRate})

    def marginSell(self, currencyPair, rate, amount, lendingRate):
        """
        Same params and output as the marginBuy-method
        """
        return self.api_query('marginSell', {'currencyPair': currencyPair, 'rate': rate, 'amount': amount, 'lendingRate': lendingRate})

    def getMarginPosition(self, currencyPair):
        """
        Returns information about your margin position in a given market.
         You may set "currencyPair" to "all" if you wish to fetch all of your margin positions at once.
         If you have no margin position in the specified market, "type" will be set to "none".
         "liquidationPrice" is an estimate, and does not necessarily represent the price at which an actual forced liquidation will occur.
         If you have no liquidation price, the value will be -1.
         {"amount":"40.94717831","total":"-0.09671314",""basePrice":"0.00236190","liquidationPrice":-1,"pl":"-0.00058655", "lendingFees":"-0.00000038","type":"long"}

         :rtype: dict
        """
        return self.api_query('getMarginPosition', {'currencyPair': currencyPair})

    def closeMarginPosition(self, currencyPair):
        """
        Closes a margin position in a given market using a market order.

        :return:
            success     0 or 1
            message
            orderID
        :rtype: dict
        """
        return self.api_query('closeMarginPosition', {'currencyPair': currencyPair})

    ## Loan methods

    def createLoanOffer(self, currency, amount, duration, autoRenew, lendingRate):
        """
        Creates a loan offer for a given currency.

        :param autoRenew: 0 or 1
        :type autoRenew: int

        :return:
            success     0 or 1
            message
            orderID
        :rtype: dict
        """
        return self.api_query('closeMarginPosition', {'currency': currency, 'amount': amount, 'duration': duration, 'autoRenew': autoRenew, 'lendingRate': lendingRate})

    def cancelLoanOffer(self, orderNumber):
        """
        Cancels a loan offer specified.

        :param orderNumber
        :type orderNumber: int

        :return:
            success     0 or 1
            message
        :rtype: dict
        """
        return self.api_query('cancelLoanOffer', {'orderNumber': orderNumber})

    def returnOpenLoanOffers(self):
        """
        Returns open loan offers for each currency.

        :rtype: dict
        """
        return self.api_query('returnOpenLoanOffers')

    def returnActiveLoans(self):
        """
        Returns active loans for each currency.

        :rtype: dict
        """
        return self.api_query('returnActiveLoans')

    def returnLendingHistory(self, start, end):
        """
        Returns lending history within a time range specified.

        :param start
        :type start: UNIX timestamp
        :param end
        :type end: UNIX timestamp
        :limit: optionally limit the numer of rows returned
        :type limit: int

        :rtype: list
        """
        return self.api_query('returnLendingHistory', {'start': start, 'end': end})

    def toggleAutoRenew(self, orderNumber):
        """
        Toggles the autoRenew setting on an active loan.

        :return:
            success     0 or 1
            message
        :rtype: dict
        """
        return self.api_query('toggleAutoRenew', {'orderNumber': orderNumber})
