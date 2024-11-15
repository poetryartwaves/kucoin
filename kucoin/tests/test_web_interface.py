# tests/test_web_interface.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from modules.interface.web_server import WebInterface
from modules.api_handler.kucoin_client import KucoinClient
from modules.market_data.market_data_fetcher import MarketDataFetcher
from modules.analysis.technical_indicators import TechnicalAnalysis
from modules.strategy.basic_strategy import BasicStrategy
from modules.risk_management.risk_manager import RiskManager
from modules.execution.position_manager import PositionManager
from modules.execution.order_manager import OrderManager
from modules.trading.trading_engine import TradingEngine
from config.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def initialize_trading_components():
    """Initialize all trading components"""
    try:
        # Initialize API client
        kucoin_client = KucoinClient()
        
        # Initialize market data fetcher
        market_data = MarketDataFetcher(kucoin_client)
        
        # Initialize technical analysis
        technical_analyzer = TechnicalAnalysis()
        
        # Initialize strategy
        strategy = BasicStrategy()
        
        # Initialize risk manager
        risk_manager = RiskManager(
            max_position_size=1000,  # Maximum position size in USDT
            max_daily_loss=100,      # Maximum daily loss in USDT
            max_trades_per_day=10,   # Maximum number of trades per day
            stop_loss_pct=2.0,       # Stop loss percentage
            take_profit_pct=4.0      # Take profit percentage
        )
        
        # Initialize order manager
        order_manager = OrderManager(kucoin_client, risk_manager)
        
        # Initialize position manager
        position_manager = PositionManager(order_manager, risk_manager)
        
        # Define trading pairs
        trading_pairs = ["BTC-USDT", "ETH-USDT"]  # Add more pairs as needed
        
        # Initialize trading engine
        trading_engine = TradingEngine(
            market_data_fetcher=market_data,
            technical_analyzer=technical_analyzer,
            strategy=strategy,
            risk_manager=risk_manager,
            position_manager=position_manager,
            trading_pairs=trading_pairs
        )
        
        return trading_engine
        
    except Exception as e:
        logging.error(f"Error initializing trading components: {str(e)}")
        raise

async def test_web_interface():
    """Test the web interface"""
    try:
        # Initialize trading components
        trading_engine = initialize_trading_components()
        
        # Initialize web interface
        web_interface = WebInterface(trading_engine)
        
        # Log test data
        logging.info("Web Interface Test Configuration:")
        logging.info(f"Trading Pairs: {trading_engine.trading_pairs}")
        logging.info(f"Risk Settings: Stop Loss: {trading_engine.risk_manager.stop_loss_pct}%, "
                    f"Take Profit: {trading_engine.risk_manager.take_profit_pct}%")
        
        # Start web server
        logging.info("\nStarting web interface...")
        web_interface.run(host='0.0.0.0', port=5000)
        
    except Exception as e:
        logging.error(f"Error testing web interface: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_web_interface())