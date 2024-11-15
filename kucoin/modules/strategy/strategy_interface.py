# modules/strategy/strategy_interface.py

from abc import ABC, abstractmethod
from typing import Dict, Any

class TradingStrategy(ABC):
    @abstractmethod
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and return trading signals"""
        pass

    @abstractmethod
    def generate_signal(self, analysis: Dict[str, Any]) -> str:
        """Generate trading signal (BUY, SELL, HOLD)"""
        pass