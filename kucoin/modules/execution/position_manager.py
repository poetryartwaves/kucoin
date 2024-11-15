# modules/execution/position_manager.py

from typing import Dict, Any
import logging

class PositionManager:
    def __init__(self, order_manager, risk_manager):
        self.order_manager = order_manager
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(__name__)
        self.positions = {}

    async def open_position(self, 
                          symbol: str, 
                          size: float, 
                          current_price: float) -> Dict[str, Any]:
        """Open a new position"""
        try:
            # Place buy order
            order = await self.order_manager.place_market_buy(
                symbol=symbol,
                size=size,
                current_price=current_price
            )

            if order:
                self.positions[symbol] = {
                    'size': size,
                    'entry_price': current_price,
                    'order_id': order['orderId']
                }
                return order
            return None

        except Exception as e:
            self.logger.error(f"Error opening position: {str(e)}")
            return None

    async def close_position(self, 
                           symbol: str, 
                           current_price: float) -> Dict[str, Any]:
        """Close an existing position"""
        try:
            if symbol not in self.positions:
                self.logger.warning(f"No open position found for {symbol}")
                return None

            position = self.positions[symbol]
            
            # Place sell order
            order = await self.order_manager.place_market_sell(
                symbol=symbol,
                size=position['size'],
                current_price=current_price
            )

            if order:
                # Calculate P&L
                pnl = (current_price - position['entry_price']) * position['size']
                self.logger.info(f"Closed position with P&L: {pnl:.2f} USDT")
                
                # Remove position
                del self.positions[symbol]
                return order
            return None

        except Exception as e:
            self.logger.error(f"Error closing position: {str(e)}")
            return None

    async def check_positions(self, current_prices: Dict[str, float]) -> None:
        """Check all open positions for exit signals"""
        try:
            for symbol in list(self.positions.keys()):
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    
                    # Check for exit signals
                    exit_signal = self.risk_manager.check_exit_signals(
                        symbol=symbol,
                        current_price=current_price
                    )
                    
                    if exit_signal:
                        self.logger.info(f"Exit signal ({exit_signal}) for {symbol}")
                        await self.close_position(symbol, current_price)

        except Exception as e:
            self.logger.error(f"Error checking positions: {str(e)}")

    def get_position_info(self, symbol: str) -> Dict[str, Any]:
        """Get information about a specific position"""
        return self.positions.get(symbol)

    def get_all_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all positions"""
        return self.positions.copy()