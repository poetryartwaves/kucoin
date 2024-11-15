# modules/market_data/market_data_fetcher.py

import logging
import time
from typing import List, Dict, Any
import pandas as pd
import numpy as np

class MarketDataFetcher:
    def __init__(self, kucoin_client):
        self.client = kucoin_client
        self.logger = logging.getLogger(__name__)

    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_ticker(symbol)
            if ticker and 'price' in ticker:
                return float(ticker['price'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None

    def get_historical_data(self, 
                          symbol: str, 
                          interval: str = '1min', 
                          lookback_hours: int = 24) -> pd.DataFrame:
        """
        Fetch historical data for given symbol and timeframe
        """
        try:
            # Calculate time range
            end_time = int(time.time() * 1000)
            start_time = end_time - (lookback_hours * 60 * 60 * 1000)

            # Fetch klines data
            klines = self.client.get_historical_klines(
                symbol=symbol,
                kline_type=interval,
                start=start_time,
                end=end_time
            )

            if not klines:
                self.logger.error(f"No klines data received for {symbol}")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'close', 'high', 
                'low', 'volume', 'turnover'
            ])

            # Convert types
            numeric_columns = ['open', 'close', 'high', 'low', 'volume', 'turnover']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert timestamp properly
            df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp', inplace=True)
            
            # Sort index to ensure chronological order
            df.sort_index(inplace=True)

            return df

        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None

    def get_24h_stats(self, symbol: str) -> Dict[str, Any]:
        """Get 24-hour statistics for a symbol"""
        try:
            stats = self.client.get_24hr_stats(symbol)
            if stats:
                return {
                    'volume': float(stats['vol']),
                    'high': float(stats['high']),
                    'low': float(stats['low']),
                    'last': float(stats['last']),
                    'change_rate': float(stats['changeRate']) * 100
                }
            return None
        except Exception as e:
            self.logger.error(f"Error getting 24h stats for {symbol}: {str(e)}")
            return None

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book for a symbol"""
        try:
            order_book = self.client.get_order_book(symbol)
            if order_book:
                return {
                    'bids': order_book['bids'][:limit],
                    'asks': order_book['asks'][:limit]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error getting order book for {symbol}: {str(e)}")
            return None