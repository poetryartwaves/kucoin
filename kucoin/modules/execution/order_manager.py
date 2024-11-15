# modules/execution/order_manager.py

from typing import Dict, Any
import logging
from decimal import Decimal, ROUND_DOWN

class OrderManager:
    def __init__(self, kucoin_client, risk_manager):
        self.client = kucoin_client
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(__name__)
        self.open_orders = {}

    def format_size(self, size: float, increment: str = '0.000001') -> str:
        """Format order size according to market rules"""
        try:
            step_size = Decimal(increment)
            size_decimal = Decimal(str(size))
            formatted_size = size_decimal.quantize(step_size, rounding=ROUND_DOWN)
            return str(formatted_size)
        except Exception as e:
            self.logger.error(f"Error formatting size: {str(e)}")
            return None

    async def place_market_buy(self, 
                             symbol: str, 
                             size: float, 
                             current_price: float) -> Dict[str, Any]:
        """Place market buy order"""
        try:
            # Check risk parameters
            trade_check = self.risk_manager.check_trade_allowed(
                symbol=symbol,
                side='buy',
                size=size,
                current_price=current_price
            )

            if not trade_check['allowed']:
                self.logger.warning(f"Trade not allowed: {trade_check['reason']}")
                return None

            # Format size according to market rules
            formatted_size = self.format_size(size)
            if not formatted_size:
                return None

            # Place order
            order = self.client.place_market_buy_order(
                symbol=symbol,
                size=formatted_size
            )

            if order:
                # Update risk manager
                self.risk_manager.update_position(
                    symbol=symbol,
                    side='buy',
                    size=float(formatted_size),
                    entry_price=current_price
                )

                # Track order
                self.open_orders[order['orderId']] = {
                    'symbol': symbol,
                    'side': 'buy',
                    'size': formatted_size,
                    'price': current_price
                }

                self.logger.info(f"Placed market buy order: {order}")
                return order

            return None

        except Exception as e:
            self.logger.error(f"Error placing market buy order: {str(e)}")
            return None

    async def place_market_sell(self, 
                              symbol: str, 
                              size: float, 
                              current_price: float) -> Dict[str, Any]:
        """Place market sell order"""
        try:
            formatted_size = self.format_size(size)
            if not formatted_size:
                return None

            order = self.client.place_market_sell_order(
                symbol=symbol,
                size=formatted_size
            )

            if order:
                # Update risk manager
                if symbol in self.risk_manager.open_positions:
                    entry_price = self.risk_manager.open_positions[symbol]['entry_price']
                    pnl = (current_price - entry_price) * float(formatted_size)
                    if pnl < 0:
                        self.risk_manager.update_daily_loss(abs(pnl))

                self.risk_manager.update_position(
                    symbol=symbol,
                    side='sell',
                    size=float(formatted_size),
                    entry_price=current_price
                )

                self.logger.info(f"Placed market sell order: {order}")
                return order

            return None

        except Exception as e:
            self.logger.error(f"Error placing market sell order: {str(e)}")
            return None

    def check_order_status(self, order_id: str) -> Dict[str, Any]:
        """Check status of an order"""
        try:
            return self.client.get_order(order_id)
        except Exception as e:
            self.logger.error(f"Error checking order status: {str(e)}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            result = self.client.cancel_order(order_id)
            if result and order_id in self.open_orders:
                del self.open_orders[order_id]
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error canceling order: {str(e)}")
            return False