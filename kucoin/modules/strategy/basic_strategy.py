# modules/strategy/basic_strategy.py

from .strategy_interface import TradingStrategy
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np

class BasicStrategy(TradingStrategy):
    def __init__(self, 
                 rsi_oversold: int = 30, 
                 rsi_overbought: int = 70,
                 ema_fast: int = 20,
                 ema_slow: int = 50):
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.logger = logging.getLogger(__name__)

    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data using multiple indicators"""
        try:
            if not market_data:
                return None

            analysis = {}
            
            # Add available signals
            if 'rsi' in market_data:
                analysis['rsi_signal'] = self._analyze_rsi(market_data['rsi'])
            
            if 'macd' in market_data:
                analysis['macd_signal'] = self._analyze_macd(market_data['macd'])
            
            if all(key in market_data for key in ['current_price', 'bollinger_bands']):
                analysis['bb_signal'] = self._analyze_bollinger_bands(
                    market_data['current_price'],
                    market_data['bollinger_bands']
                )
            
            if all(key in market_data for key in ['ema_20', 'ema_50']):
                analysis['ema_signal'] = self._analyze_ema_cross(
                    market_data['ema_20'],
                    market_data['ema_50']
                )

            analysis['current_price'] = market_data.get('current_price', 0)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {str(e)}")
            return None

    def generate_signal(self, analysis: Dict[str, Any]) -> str:
        """Generate trading signal based on combined analysis"""
        try:
            if not analysis:
                return "HOLD"

            signals = []
            
            # Collect available signals
            if 'rsi_signal' in analysis:
                signals.append(analysis['rsi_signal'])
            
            if 'macd_signal' in analysis:
                signals.append(analysis['macd_signal'])
            
            if 'bb_signal' in analysis:
                signals.append(analysis['bb_signal'])
            
            if 'ema_signal' in analysis:
                signals.append(analysis['ema_signal'])

            if not signals:
                return "HOLD"

            # Count signals
            buy_count = signals.count("BUY")
            sell_count = signals.count("SELL")
            
            # Generate final signal
            if buy_count > len(signals) / 2:
                return "BUY"
            elif sell_count > len(signals) / 2:
                return "SELL"
            return "HOLD"

        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return "HOLD"

    def _analyze_rsi(self, rsi: float) -> str:
        """Analyze RSI indicator"""
        try:
            if pd.isna(rsi):
                return "HOLD"
            
            if rsi <= self.rsi_oversold:
                return "BUY"
            elif rsi >= self.rsi_overbought:
                return "SELL"
            return "HOLD"
        except Exception as e:
            self.logger.error(f"Error analyzing RSI: {str(e)}")
            return "HOLD"

    def _analyze_macd(self, macd_data: Dict) -> str:
        """Analyze MACD indicator"""
        try:
            if not isinstance(macd_data, dict):
                return "HOLD"
                
            macd_line = macd_data['macd'].iloc[-1]
            signal_line = macd_data['signal'].iloc[-1]
            
            if pd.isna(macd_line) or pd.isna(signal_line):
                return "HOLD"
            
            if macd_line > signal_line:
                return "BUY"
            elif macd_line < signal_line:
                return "SELL"
            return "HOLD"
        except Exception as e:
            self.logger.error(f"Error analyzing MACD: {str(e)}")
            return "HOLD"

    def _analyze_bollinger_bands(self, current_price: float, bb_data: Dict) -> str:
        """Analyze Bollinger Bands"""
        try:
            if not isinstance(bb_data, dict):
                return "HOLD"
                
            upper = bb_data['upper'].iloc[-1]
            lower = bb_data['lower'].iloc[-1]
            
            if pd.isna(upper) or pd.isna(lower) or pd.isna(current_price):
                return "HOLD"
            
            if current_price <= lower:
                return "BUY"
            elif current_price >= upper:
                return "SELL"
            return "HOLD"
        except Exception as e:
            self.logger.error(f"Error analyzing Bollinger Bands: {str(e)}")
            return "HOLD"

    def _analyze_ema_cross(self, ema_fast: float, ema_slow: float) -> str:
        """Analyze EMA cross"""
        try:
            if pd.isna(ema_fast) or pd.isna(ema_slow):
                return "HOLD"
                
            if ema_fast > ema_slow:
                return "BUY"
            elif ema_fast < ema_slow:
                return "SELL"
            return "HOLD"
        except Exception as e:
            self.logger.error(f"Error analyzing EMA cross: {str(e)}")
            return "HOLD"