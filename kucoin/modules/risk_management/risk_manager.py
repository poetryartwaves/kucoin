# modules/risk_management/risk_manager.py

from typing import Dict, Any
import logging

class RiskManager:
    def __init__(self, 
                 max_position_size: float,
                 max_daily_loss: float,
                 max_trades_per_day: int,
                 stop_loss_pct: float,
                 take_profit_pct: float):
        """
        Initialize Risk Manager
        
        Parameters:
        - max_position_size: Maximum position size in USDT
        - max_daily_loss: Maximum daily loss allowed in USDT
        - max_trades_per_day: Maximum number of trades per day
        - stop_loss_pct: Stop loss percentage
        - take_profit_pct: Take profit percentage
        """
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_trades_per_day = max_trades_per_day
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        
        self.daily_loss = 0
        self.daily_trades = 0
        self.open_positions = {}
        self.logger = logging.getLogger(__name__)

    def calculate_position_size(self, 
                              account_balance: float, 
                              current_price: float,
                              risk_per_trade: float = 0.02) -> float:
        """Calculate safe position size based on account balance and risk"""
        try:
            # Calculate position size based on risk percentage
            risk_amount = account_balance * risk_per_trade
            position_size = min(
                risk_amount / (current_price * (self.stop_loss_pct / 100)),
                self.max_position_size / current_price
            )
            
            return position_size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0

    def check_trade_allowed(self, 
                          symbol: str, 
                          side: str, 
                          size: float, 
                          current_price: float) -> Dict[str, Any]:
        """Check if trade is allowed based on risk parameters"""
        try:
            if self.daily_trades >= self.max_trades_per_day:
                return {
                    'allowed': False,
                    'reason': 'Maximum daily trades reached'
                }
            
            if self.daily_loss >= self.max_daily_loss:
                return {
                    'allowed': False,
                    'reason': 'Maximum daily loss reached'
                }
            
            position_value = size * current_price
            if position_value > self.max_position_size:
                return {
                    'allowed': False,
                    'reason': 'Position size exceeds maximum allowed'
                }
            
            return {
                'allowed': True,
                'stop_loss': current_price * (1 - self.stop_loss_pct/100),
                'take_profit': current_price * (1 + self.take_profit_pct/100)
            }
            
        except Exception as e:
            self.logger.error(f"Error checking trade allowance: {str(e)}")
            return {'allowed': False, 'reason': str(e)}

    def update_position(self, 
                       symbol: str, 
                       side: str, 
                       size: float, 
                       entry_price: float) -> None:
        """Update position tracking"""
        try:
            if side == 'buy':
                self.open_positions[symbol] = {
                    'size': size,
                    'entry_price': entry_price,
                    'stop_loss': entry_price * (1 - self.stop_loss_pct/100),
                    'take_profit': entry_price * (1 + self.take_profit_pct/100)
                }
            elif side == 'sell' and symbol in self.open_positions:
                del self.open_positions[symbol]
                
            self.daily_trades += 1
            
        except Exception as e:
            self.logger.error(f"Error updating position: {str(e)}")

    def check_exit_signals(self, symbol: str, current_price: float) -> str:
        """Check if position should be closed based on SL/TP"""
        try:
            if symbol not in self.open_positions:
                return None
                
            position = self.open_positions[symbol]
            
            if current_price <= position['stop_loss']:
                return 'stop_loss'
            elif current_price >= position['take_profit']:
                return 'take_profit'
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking exit signals: {str(e)}")
            return None

    def update_daily_loss(self, loss_amount: float) -> None:
        """Update daily loss tracker"""
        self.daily_loss += loss_amount

    def reset_daily_metrics(self) -> None:
        """Reset daily tracking metrics"""
        self.daily_loss = 0
        self.daily_trades = 0