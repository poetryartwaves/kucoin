# tests/test_execution.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import asyncio
from modules.api_handler.kucoin_client import KucoinClient
from modules.market_data.market_data_fetcher import MarketDataFetcher
from modules.risk_management.risk_manager import RiskManager
from modules.execution.order_manager import OrderManager
from modules.execution.position_manager import PositionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_execution():
    try:
        # Initialize components
        kucoin_client = KucoinClient()
        market_data = MarketDataFetcher(kucoin_client)
        
        risk_manager = RiskManager(
            max_position_size=1000,
            max_daily_loss=100,
            max_trades_per_day=10,
            stop_loss_pct=2.0,
            take_profit_pct=4.0
        )
        
        order_manager = OrderManager(kucoin_client, risk_manager)
        position_manager = PositionManager(order_manager, risk_manager)
        
        symbol = "BTC-USDT"
        
        # Get current price
        current_price = market_data.get_current_price(symbol)
        
        if current_price:
            logging.info(f"\nTesting execution system for {symbol}")
            logging.info(f"Current Price: ${current_price:.2f}")
            
            # Calculate test position size (very small for testing)
            position_size = 0.001  # Minimum size for testing
            
            # Test opening position
            logging.info("\nTesting position opening...")
            open_order = await position_manager.open_position(
                symbol=symbol,
                size=position_size,
                current_price=current_price
            )
            
            if open_order:
                logging.info(f"Position opened: {open_order}")
                
                # Wait a few seconds
                await asyncio.sleep(5)
                
                # Test closing position
                logging.info("\nTesting position closing...")
                close_order = await position_manager.close_position(
                    symbol=symbol,
                    current_price=current_price
                )
                
                if close_order:
                    logging.info(f"Position closed: {close_order}")
                else:
                    logging.error("Failed to close position")
            else:
                logging.error("Failed to open position")
                
        else:
            logging.error("Failed to get current price")
            
    except Exception as e:
        logging.error(f"Error in execution test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_execution())