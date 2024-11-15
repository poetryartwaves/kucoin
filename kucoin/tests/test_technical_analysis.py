# tests/test_technical_analysis.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from modules.api_handler.kucoin_client import KucoinClient
from modules.analysis.technical_indicators import TechnicalAnalysis
from modules.market_data.market_data_fetcher import MarketDataFetcher
from config.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_market_analysis():
    try:
        # Initialize components
        kucoin_client = KucoinClient()
        market_data = MarketDataFetcher(kucoin_client)
        ta = TechnicalAnalysis()
        
        symbol = "BTC-USDT"
        
        # Get market summary
        summary = market_data.get_market_summary(symbol)
        if summary:
            logging.info("\nMarket Summary:")
            for key, value in summary.items():
                logging.info(f"{key}: {value}")

        # Get historical data
        df = market_data.get_historical_data(
            symbol=symbol,
            interval='1min',
            lookback_hours=24
        )
        
        if df is not None:
            logging.info(f"\nReceived {len(df)} candlesticks")
            
            # Perform technical analysis
            analysis = ta.get_market_analysis(df)
            
            if analysis:
                logging.info(f"\nTechnical Analysis for {symbol}:")
                logging.info(f"Current Price: {analysis['current_price']:.2f}")
                logging.info(f"RSI: {analysis['rsi']:.2f}")
                logging.info(f"EMA20: {analysis['ema_20']:.2f}")
                logging.info(f"EMA50: {analysis['ema_50']:.2f}")
                
                # MACD values
                last_macd = analysis['macd']['macd'].iloc[-1]
                last_signal = analysis['macd']['signal'].iloc[-1]
                logging.info(f"MACD: {last_macd:.2f}")
                logging.info(f"Signal: {last_signal:.2f}")
                
                # Bollinger Bands
                bb = analysis['bollinger_bands']
                logging.info(f"Bollinger Bands:")
                logging.info(f"Upper: {bb['upper'].iloc[-1]:.2f}")
                logging.info(f"Middle: {bb['middle'].iloc[-1]:.2f}")
                logging.info(f"Lower: {bb['lower'].iloc[-1]:.2f}")
        else:
            logging.error("Failed to retrieve historical data")
            
    except Exception as e:
        logging.error(f"Error in market analysis test: {str(e)}")

if __name__ == "__main__":
    test_market_analysis()