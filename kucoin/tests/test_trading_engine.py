# tests/test_trading_engine.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import asyncio
from modules.api_handler.kucoin_client import KucoinClient
from modules.market_data.market_data_fetcher import MarketDataFetcher
from modules.analysis.technical_indicators import TechnicalAnalysis
from modules.strategy.basic_strategy import BasicStrategy
from modules.risk_management.risk_manager import RiskManager
from modules.execution.position_manager import PositionManager
from modules.execution.order_manager import OrderManager
from modules.trading.trading_engine import TradingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_trading_engine():
    try:
        # Initialize components
        kucoin_client = KucoinClient()
        market_data = MarketDataFetcher(kucoin_client)
        technical_analysis = TechnicalAnalysis()
        strategy = BasicStrategy()
        
        risk_manager = RiskManager(
            max_position_size=1000,
            max_daily_loss=100,
            max_trades_per_day=10,
            stop_loss_pct=2.0,
            take_profit_pct=4.0
        )
        
        order_manager = OrderManager(kucoin_client, risk_manager)
        position_manager = PositionManager(order_manager, risk_manager)
        
        trading_pairs = ["BTC-USDT", "ETH-USDT"]
        
        # Initialize trading engine
        engine = TradingEngine(
            market_data_fetcher=market_data,
            technical_analyzer=technical_analysis,
            strategy=strategy,
            risk_manager=risk_manager,
            position_manager=position_manager,
            trading_pairs=trading_pairs
        )
        
        # Run engine for test period
        logging.info("Starting trading engine test...")
        
        # Run for 5 minutes
        engine_task = asyncio.create_task(engine.run())
        await asyncio.sleep(300)  # 5 minutes
        
        # Stop engine
        engine.stop()
        await engine_task
        
        # Print results
        logging.info("\nTrading Test Results:")
        logging.info(f"Total Trades: {engine.daily_stats['trades']}")
        logging.info(f"Trade History: {len(engine.trades_history)} entries")
        
    except Exception as e:
        logging.error(f"Error in trading engine test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_trading_engine())