# modules/api_handler/kucoin_client.py

from kucoin.client import Client
from config.config import Config
import logging

class KucoinClient:
    def __init__(self):
        try:
            self.client = Client(
                Config.API_KEY,
                Config.API_SECRET,
                Config.API_PASSPHRASE,
                sandbox=False  # Using live platform
            )
            logging.info("Successfully connected to Kucoin API")
            
        except Exception as e:
            logging.error(f"Failed to initialize Kucoin client: {str(e)}")
            raise

    def get_ticker(self, symbol):
        """Get current ticker information for a symbol"""
        try:
            return self.client.get_ticker(symbol)
        except Exception as e:
            logging.error(f"Error getting ticker for {symbol}: {str(e)}")
            return None

    def get_account_balance(self):
        """Get account balances"""
        try:
            return self.client.get_accounts()
        except Exception as e:
            logging.error(f"Error getting account balance: {str(e)}")
            return None

    def place_market_buy_order(self, symbol, size):
        """Place a market buy order"""
        try:
            return self.client.create_market_order(
                symbol=symbol,
                side='buy',
                size=str(size)
            )
        except Exception as e:
            logging.error(f"Error placing market buy order: {str(e)}")
            return None

    def place_market_sell_order(self, symbol, size):
        """Place a market sell order"""
        try:
            return self.client.create_market_order(
                symbol=symbol,
                side='sell',
                size=str(size)
            )
        except Exception as e:
            logging.error(f"Error placing market sell order: {str(e)}")
            return None

    def get_order_book(self, symbol):
        """Get order book for a symbol"""
        try:
            return self.client.get_order_book(symbol)
        except Exception as e:
            logging.error(f"Error getting order book for {symbol}: {str(e)}")
            return None


    def get_historical_klines(self, symbol, kline_type='1min', start=None, end=None):
        """Get historical kline data"""
        try:
        # Convert timestamps if provided
           start_ts = int(start/1000) if start else None
           end_ts = int(end/1000) if end else None
        
           # Use get_kline_data method with correct parameter names
           return self.client.get_kline_data(
               symbol=symbol,
               kline_type=kline_type,
               start=start_ts,    # Changed from startAt to start
               end=end_ts        # Changed from endAt to end
           )
        except Exception as e:
            logging.error(f"Error getting historical klines: {str(e)}")
            return None

    def get_24hr_stats(self, symbol):
        """Get 24hr stats for a symbol"""
        try:
            return self.client.get_24hr_stats(symbol)
        except Exception as e:
            logging.error(f"Error getting 24hr stats for {symbol}: {str(e)}")
            return None

    def get_currencies(self):
        """Get list of currencies"""
        try:
            return self.client.get_currencies()
        except Exception as e:
            logging.error(f"Error getting currencies: {str(e)}")
            return None