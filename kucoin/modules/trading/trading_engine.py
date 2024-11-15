# modules/trading/trading_engine.py

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
import pandas as pd
import numpy as np
from modules.interface.web_server import WebInterface
from modules.notifications.notification_handler import NotificationHandler
from config.config import Config

class TradingEngine:
    def __init__(self, 
                 market_data_fetcher,
                 technical_analyzer,
                 strategy,
                 risk_manager,
                 position_manager,
                 trading_pairs: list):
        """
        Initialize Trading Engine
        
        Parameters:
        - market_data_fetcher: MarketDataFetcher instance
        - technical_analyzer: TechnicalAnalysis instance
        - strategy: Trading strategy instance
        - risk_manager: RiskManager instance
        - position_manager: PositionManager instance
        - trading_pairs: List of trading pairs to monitor
        """
        # Core components
        self.market_data = market_data_fetcher
        self.analyzer = technical_analyzer
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.position_manager = position_manager
        self.trading_pairs = trading_pairs
        
        # Control flags
        self.is_running = False
        self.start_time = None
        
        # Performance tracking
        self.trades_history = []
        self.daily_stats = {
            'trades': 0,
            'pnl': 0.0,
            'wins': 0,
            'losses': 0
        }
        
        # Enhanced performance metrics
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'win_rate': 0.0,
            'risk_reward_ratio': 0.0
        }
        
        # Trading parameters
        self.min_trade_interval = Config.MIN_TRADE_INTERVAL
        self.last_trade_time = {}
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize notification system
        self.notification_handler = NotificationHandler()
        self.last_performance_notification = datetime.now()
        
        # Initialize web interface
        self.web_interface = WebInterface(self)
        self.web_thread = None

    async def validate_trade_conditions(self, 
                                     symbol: str, 
                                     signal: str, 
                                     current_price: float) -> bool:
        """Validate all conditions before trading"""
        try:
            # Check trading interval
            if symbol in self.last_trade_time:
                time_since_last_trade = (datetime.now() - 
                                       self.last_trade_time[symbol]).total_seconds()
                if time_since_last_trade < self.min_trade_interval:
                    return False

            # Check market volatility
            volatility = await self.calculate_volatility(symbol)
            if volatility > Config.MAX_VOLATILITY:
                self.logger.warning(f"High volatility for {symbol}: {volatility}")
                return False

            # Check trading volume
            volume = await self.get_24h_volume(symbol)
            if volume < Config.MIN_VOLUME:
                return False

            # Check spread
            spread = await self.get_current_spread(symbol)
            if spread > Config.MAX_SPREAD:
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating trade conditions: {str(e)}")
            return False

    async def calculate_volatility(self, symbol: str, period: int = 14) -> float:
        """Calculate current market volatility"""
        try:
            df = self.market_data.get_historical_data(
                symbol=symbol,
                interval='1min',
                lookback_hours=1
            )
            if df is not None:
                returns = np.log(df['close'] / df['close'].shift(1))
                return returns.std() * np.sqrt(period)
            return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 0.0

    async def get_24h_volume(self, symbol: str) -> float:
        """Get 24-hour trading volume"""
        try:
            stats = self.market_data.get_24h_stats(symbol)
            return float(stats['volume']) if stats else 0.0
        except Exception as e:
            self.logger.error(f"Error getting 24h volume: {str(e)}")
            return 0.0

    async def get_current_spread(self, symbol: str) -> float:
        """Calculate current bid-ask spread"""
        try:
            order_book = self.market_data.get_order_book(symbol)
            if order_book and order_book['bids'] and order_book['asks']:
                best_bid = float(order_book['bids'][0][0])
                best_ask = float(order_book['asks'][0][0])
                return (best_ask - best_bid) / best_bid * 100
            return 0.0
        except Exception as e:
            self.logger.error(f"Error calculating spread: {str(e)}")
            return 0.0

    async def process_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Process a single trading pair"""
        try:
            # Get market data
            df = self.market_data.get_historical_data(
                symbol=symbol,
                interval='1min',
                lookback_hours=24
            )
            
            if df is None:
                return None
            
            # Get current price
            current_price = self.market_data.get_current_price(symbol)
            if not current_price:
                return None
                
            # Perform technical analysis
            analysis = self.analyzer.get_market_analysis(df)
            if not analysis:
                return None
                
            # Generate trading signal
            signal = self.strategy.generate_signal(analysis)
            
            # Process signal with validation
            if await self.validate_trade_conditions(symbol, signal, current_price):
                await self.process_signal(symbol, signal, current_price, analysis)
            
            # Check existing positions
            await self.check_positions(symbol, current_price)
            
            # Prepare market data for web interface and notifications
            market_data = {
                'symbol': symbol,
                'current_price': current_price,
                'signal': signal,
                'rsi': analysis.get('rsi'),
                'macd': analysis.get('macd', {}).get('macd', {}).get('value'),
                'ema_fast': analysis.get('ema_20'),
                'ema_slow': analysis.get('ema_50'),
                'timestamp': datetime.now().isoformat(),
                'volatility': await self.calculate_volatility(symbol),
                'volume_24h': await self.get_24h_volume(symbol),
                'spread': await self.get_current_spread(symbol)
            }
            
            # Update web interface with market data
            self.web_interface.update_market_data(symbol, market_data)
            
            return market_data
            
        except Exception as e:
            error_msg = f"Error processing symbol {symbol}: {str(e)}"
            self.logger.error(error_msg)
            self.notification_handler.notify_error(error_msg)
            return None

    async def process_signal(self, 
                           symbol: str, 
                           signal: str, 
                           current_price: float,
                           analysis: Dict[str, Any]) -> None:
        """Process trading signal"""
        try:
            position = self.position_manager.get_position_info(symbol)
            
            if signal == "BUY" and not position:
                account_balance = await self.get_account_balance()
                size = self.risk_manager.calculate_position_size(
                    account_balance=account_balance,
                    current_price=current_price
                )
                
                if size > 0:
                    order = await self.position_manager.open_position(
                        symbol=symbol,
                        size=size,
                        current_price=current_price
                    )
                    
                    if order:
                        self.last_trade_time[symbol] = datetime.now()
                        self.logger.info(f"Opened position for {symbol} at {current_price}")
                        self.record_trade('open', symbol, current_price, size)
                        
                        # Send notification
                        self.notification_handler.notify_trade({
                            'type': 'BUY',
                            'symbol': symbol,
                            'price': current_price,
                            'size': size,
                            'timestamp': datetime.now()
                        })
                        
            elif signal == "SELL" and position:
                order = await self.position_manager.close_position(
                    symbol=symbol,
                    current_price=current_price
                )
                
                if order:
                    self.last_trade_time[symbol] = datetime.now()
                    pnl = (current_price - position['entry_price']) * position['size']
                    self.logger.info(f"Closed position for {symbol} at {current_price}, PnL: {pnl:.2f}")
                    self.record_trade('close', symbol, current_price, position['size'], pnl)
                    
                    # Send notification
                    self.notification_handler.notify_trade({
                        'type': 'SELL',
                        'symbol': symbol,
                        'price': current_price,
                        'size': position['size'],
                        'pnl': pnl,
                        'timestamp': datetime.now()
                    })
                    
        except Exception as e:
            error_msg = f"Error processing signal for {symbol}: {str(e)}"
            self.logger.error(error_msg)
            self.notification_handler.notify_error(error_msg)

    def record_trade(self, 
                    trade_type: str, 
                    symbol: str, 
                    price: float, 
                    size: float,
                    pnl: float = None) -> None:
        """Record trade for performance tracking"""
        try:
            trade = {
                'timestamp': datetime.now(),
                'type': trade_type,
                'symbol': symbol,
                'price': price,
                'size': size,
                'pnl': pnl
            }
            
            self.trades_history.append(trade)
            self.daily_stats['trades'] += 1
            
            if trade_type == 'close' and pnl is not None:
                self.daily_stats['pnl'] += pnl
                if pnl > 0:
                    self.daily_stats['wins'] += 1
                else:
                    self.daily_stats['losses'] += 1
                
                # Update enhanced performance metrics
                self.update_performance_metrics(trade)
            
            # Update web interface and send notification
            self.web_interface.log_trade(trade)
            self.notification_handler.notify_trade(trade)
            
        except Exception as e:
            self.logger.error(f"Error recording trade: {str(e)}")

    def update_performance_metrics(self, trade: Dict[str, Any]) -> None:
        """Update detailed performance metrics"""
        try:
            if 'pnl' in trade and trade['pnl'] is not None:
                self.performance_metrics['total_trades'] += 1
                self.performance_metrics['total_pnl'] += trade['pnl']

                if trade['pnl'] > 0:
                    self.performance_metrics['winning_trades'] += 1
                    self.performance_metrics['largest_win'] = max(
                        self.performance_metrics['largest_win'], 
                        trade['pnl']
                    )
                else:
                    self.performance_metrics['losing_trades'] += 1
                    self.performance_metrics['largest_loss'] = min(
                        self.performance_metrics['largest_loss'], 
                        trade['pnl']
                    )

                # Update averages and ratios
                if self.performance_metrics['winning_trades'] > 0:
                    self.performance_metrics['average_win'] = (
                        self.performance_metrics['total_pnl'] / 
                        self.performance_metrics['winning_trades']
                    )

                if self.performance_metrics['losing_trades'] > 0:
                    self.performance_metrics['average_loss'] = (
                        abs(self.performance_metrics['total_pnl']) / 
                        self.performance_metrics['losing_trades']
                    )

                total_trades = self.performance_metrics['total_trades']
                if total_trades > 0:
                    self.performance_metrics['win_rate'] = (
                        self.performance_metrics['winning_trades'] / 
                        total_trades * 100
                    )

                if self.performance_metrics['average_loss'] != 0:
                    self.performance_metrics['risk_reward_ratio'] = (
                        abs(self.performance_metrics['average_win'] / 
                            self.performance_metrics['average_loss'])
                    )

        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")

    async def run(self) -> None:
        """Main trading loop"""
        self.is_running = True
        self.start_time = datetime.now()
        self.logger.info("Starting trading engine...")
        
        # Notify start
        self.notification_handler.notify(
            "🚀 Trading Bot Started\nMonitoring markets...",
            level='important'
        )
        
        # Start web interface
        self.web_thread = threading.Thread(
            target=self.web_interface.run,
            kwargs={'host': '0.0.0.0', 'port': 5000}
        )
        self.web_thread.start()
        
        while self.is_running:
            try:
                # Process each trading pair
                for symbol in self.trading_pairs:
                    market_data = await self.process_symbol(symbol)
                    if market_data:
                        self.web_interface.update_market_data(symbol, market_data)
                
                # Update positions
                positions = self.position_manager.get_all_positions()
                for symbol, position in positions.items():
                    self.web_interface.update_position(symbol, position)
                
                # Send performance notification if interval elapsed
                now = datetime.now()
                if (now - self.last_performance_notification).total_seconds() >= Config.PERFORMANCE_NOTIFICATION_INTERVAL:
                    metrics = self.get_performance_metrics()
                    self.notification_handler.notify_performance(metrics)
                    self.last_performance_notification = now
                
                # Reset daily metrics at midnight
                if now.hour == 0 and now.minute == 0:
                    self.risk_manager.reset_daily_metrics()
                    self.daily_stats = {
                        'trades': 0,
                        'pnl': 0.0,
                        'wins': 0,
                        'losses': 0
                    }
                    self.notification_handler.notify(
                        "📊 Daily metrics reset",
                        level='info'
                    )
                
                await asyncio.sleep(60)  # 1-minute interval
                
            except Exception as e:
                error_msg = f"Error in main trading loop: {str(e)}"
                self.logger.error(error_msg)
                self.notification_handler.notify_error(error_msg)
                await asyncio.sleep(60)

    def stop(self) -> None:
        """Stop the trading engine"""
        self.is_running = False
        self.logger.info("Stopping trading engine...")
        
        # Send stop notification
        self.notification_handler.notify(
            "🛑 Trading Bot Stopped\nAll operations ceased.",
            level='important'
        )
        
        # Cleanup web interface
        if self.web_thread:
            self.web_thread.join()    