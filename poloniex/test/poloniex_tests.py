import unittest
from poloniex.poloniex import Poloniex

def test_public_response(unit_test, result, method_name):
    unit_test.assertTrue(isinstance(result, dict), 'result is not a dict')
    unit_test.assertFalse('error' in result, '{0:s} failed'.format(method_name))


class TestPublicAPI(unittest.TestCase):

    def setUp(self):
        self.poloniex = Poloniex()

    def test_get_volume(self):
        actual = self.poloniex.return24hVolume()
        test_public_response(self, actual, "return24hVolume")

    def test_get_currencies(self):
        actual = self.poloniex.returnCurrencies()
        test_public_response(self, actual, "getCurrencies")
        pass


class TestTradingAPI(unittest.TestCase):
    def setUp(self):
        self.poloniex = Poloniex()

    def test_key_and_secret(self):
        self.poloniex = Poloniex(None, None)
        actual = self.poloniex.returnBalances()
        self.assertTrue('error' in actual, "failed with None key and None secret")

        self.poloniex = Poloniex("123", None)
        actual = self.poloniex.returnBalances()
        self.assertTrue('error' in actual, "failed with None secret")

        self.poloniex = Poloniex(None, "123")
        actual = self.poloniex.returnBalances()
        self.assertTrue('error' in actual, "failed with None key")

    def test_load_key_and_secret(self):
        self.poloniex.load_key('poloniex/test/secrets.json')
        actual = self.poloniex.returnBalances()
        self.assertFalse('error' in actual, "failed with missing/wrong key or secret")


if __name__ == '__main__':
    unittest.main()
