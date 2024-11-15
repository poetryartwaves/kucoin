# modules/analysis/technical_indicators.py

import numpy as np
import pandas as pd
import logging
from typing import Dict, Any

class TechnicalAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def prepare_dataframe(self, klines_data: list) -> pd.DataFrame:
        """Convert klines data to DataFrame"""
        try:
            df = pd.DataFrame(klines_data, columns=[
                'timestamp', 'open', 'close', 'high', 
                'low', 'volume', 'turnover'
            ])
            
            # Convert strings to numeric
            for col in ['open', 'close', 'high', 'low', 'volume', 'turnover']:
                df[col] = pd.to_numeric(df[col])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        except Exception as e:
            self.logger.error(f"Error preparing DataFrame: {str(e)}")
            return None

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return None

    def calculate_macd(self, df: pd.DataFrame, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        try:
            exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=signal_period, adjust=False).mean()
            histogram = macd - signal
            
            return {
                'macd': macd,
                'signal': signal,
                'histogram': histogram
            }
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {str(e)}")
            return None

    def calculate_bollinger_bands(self, df: pd.DataFrame, 
                                period: int = 20, 
                                std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        try:
            middle_band = df['close'].rolling(window=period).mean()
            std = df['close'].rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return {
                'upper': upper_band,
                'middle': middle_band,
                'lower': lower_band
            }
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None

    def calculate_ema(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        try:
            return df['close'].ewm(span=period, adjust=False).mean()
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {str(e)}")
            return None

    def get_market_analysis(self, klines_data: list) -> Dict[str, Any]:
        """Perform complete market analysis"""
        try:
            df = self.prepare_dataframe(klines_data)
            if df is None:
                return None

            analysis = {
                'rsi': self.calculate_rsi(df).iloc[-1],
                'macd': self.calculate_macd(df),
                'bollinger_bands': self.calculate_bollinger_bands(df),
                'ema_20': self.calculate_ema(df, 20).iloc[-1],
                'ema_50': self.calculate_ema(df, 50).iloc[-1],
                'current_price': df['close'].iloc[-1],
                'volume': df['volume'].iloc[-1]
            }

            return analysis
        except Exception as e:
            self.logger.error(f"Error performing market analysis: {str(e)}")
            return None