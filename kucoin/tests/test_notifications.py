# C:\kucoin\tests\test_notifications.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime
from modules.notifications.notification_handler import NotificationHandler
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_notifications():
    """Test different types of notifications"""
    try:
        # Initialize notification handler
        handler = NotificationHandler()
        
        # Test basic notification
        logging.info("Testing basic notification...")
        handler.notify("Test notification message", level='info')
        
        # Test trade notification
        logging.info("Testing trade notification...")
        test_trade = {
            'type': 'BUY',
            'symbol': 'BTC-USDT',
            'price': 50000.00,
            'size': 0.1,
            'timestamp': datetime.now(),
            'pnl': None
        }
        handler.notify_trade(test_trade)
        
        logging.info("Notification tests completed!")
        
    except Exception as e:
        logging.error(f"Error in notification test: {str(e)}")
        raise

if __name__ == "__main__":
    test_notifications()