# tests/test_strategy.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from modules.api_handler.kucoin_client import KucoinClient
from modules.analysis.technical_indicators import TechnicalAnalysis
from modules.market_data.market_data_fetcher import MarketDataFetcher
from modules.strategy.basic_strategy import BasicStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_strategy():
    try:
        # Initialize components
        kucoin_client = KucoinClient()
        market_data = MarketDataFetcher(kucoin_client)
        ta = TechnicalAnalysis()
        strategy = BasicStrategy()
        
        symbol = "BTC-USDT"
        
        # Get market data
        df = market_data.get_historical_data(
            symbol=symbol,
            interval='1min',
            lookback_hours=24
        )
        
        if df is not None:
            # Get technical analysis
            analysis = ta.get_market_analysis(df)
            
            if analysis:
                # Get strategy analysis
                strategy_analysis = strategy.analyze(analysis)
                signal = strategy.generate_signal(strategy_analysis)
                
                # Log results
                logging.info(f"\nStrategy Analysis for {symbol}:")
                logging.info(f"Current Price: ${analysis['current_price']:.2f}")
                logging.info(f"RSI Signal: {strategy_analysis['rsi_signal']}")
                logging.info(f"MACD Signal: {strategy_analysis['macd_signal']}")
                logging.info(f"Bollinger Bands Signal: {strategy_analysis['bb_signal']}")
                logging.info(f"EMA Signal: {strategy_analysis['ema_signal']}")
                logging.info(f"\nFinal Signal: {signal}")
                
        else:
            logging.error("Failed to retrieve market data")
            
    except Exception as e:
        logging.error(f"Error in strategy test: {str(e)}")

if __name__ == "__main__":
    test_strategy()