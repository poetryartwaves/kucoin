import os
import sys
import logging
from pathlib import Path

# Add the project root directory to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config.config import Config
from modules.api_handler.kucoin_client import KucoinClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_configuration():
    try:
        # Validate configuration
        Config.validate_config()
        logging.info("Configuration validation successful")
        
        # Print configuration (excluding sensitive data)
        logging.info("\nCurrent Configuration:")
        logging.info(f"Trading Pairs: {Config.TRADING_PAIRS}")
        logging.info(f"Max Position Size: {Config.MAX_POSITION_SIZE} USDT")
        logging.info(f"Stop Loss: {Config.STOP_LOSS_PERCENTAGE}%")
        logging.info(f"Take Profit: {Config.TAKE_PROFIT_PERCENTAGE}%")
        logging.info(f"Max Trades Per Day: {Config.MAX_TRADES_PER_DAY}")
        logging.info(f"Trading Timeframe: {Config.TRADING_TIMEFRAME}")
        
        # Test API connection with new config
        client = KucoinClient()
        
        # Test getting balance
        balance = client.get_account_balance()
        logging.info("\nAccount Balance:")
        logging.info(balance)
        
        # Test getting tickers for configured trading pairs
        logging.info("\nCurrent Prices:")
        for pair in Config.TRADING_PAIRS:
            ticker = client.get_ticker(pair)
            logging.info(f"{pair}: {ticker}")
            
    except Exception as e:
        logging.error(f"Configuration test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_configuration()