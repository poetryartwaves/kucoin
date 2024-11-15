# tests/test_risk_manager.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from modules.risk_management.risk_manager import RiskManager
from modules.api_handler.kucoin_client import KucoinClient
from modules.market_data.market_data_fetcher import MarketDataFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_risk_manager():
    try:
        # Initialize components
        kucoin_client = KucoinClient()
        market_data = MarketDataFetcher(kucoin_client)
        
        # Initialize Risk Manager
        risk_manager = RiskManager(
            max_position_size=1000,  # 1000 USDT
            max_daily_loss=100,      # 100 USDT
            max_trades_per_day=10,
            stop_loss_pct=2.0,
            take_profit_pct=4.0
        )
        
        symbol = "BTC-USDT"
        
        # Get current price
        current_price = market_data.get_current_price(symbol)
        
        if current_price:
            # Test position size calculation
            account_balance = 10000  # Example balance
            position_size = risk_manager.calculate_position_size(
                account_balance=account_balance,
                current_price=current_price
            )
            
            logging.info("\nRisk Management Test:")
            logging.info(f"Current Price: ${current_price:.2f}")
            logging.info(f"Recommended Position Size: {position_size:.6f} BTC")
            logging.info(f"Position Value: ${position_size * current_price:.2f}")
            
            # Test trade allowance
            trade_check = risk_manager.check_trade_allowed(
                symbol=symbol,
                side='buy',
                size=position_size,
                current_price=current_price
            )
            
            logging.info("\nTrade Check:")
            logging.info(f"Trade Allowed: {trade_check['allowed']}")
            if trade_check['allowed']:
                logging.info(f"Stop Loss: ${trade_check['stop_loss']:.2f}")
                logging.info(f"Take Profit: ${trade_check['take_profit']:.2f}")
            else:
                logging.info(f"Reason: {trade_check['reason']}")
            
            # Test position tracking
            if trade_check['allowed']:
                risk_manager.update_position(
                    symbol=symbol,
                    side='buy',
                    size=position_size,
                    entry_price=current_price
                )
                
                # Test exit signals
                exit_signal = risk_manager.check_exit_signals(
                    symbol=symbol,
                    current_price=current_price * 0.98  # Simulate price drop
                )
                
                logging.info("\nExit Signal Test:")
                logging.info(f"Exit Signal: {exit_signal}")
                
        else:
            logging.error("Failed to get current price")
            
    except Exception as e:
        logging.error(f"Error in risk manager test: {str(e)}")

if __name__ == "__main__":
    test_risk_manager()