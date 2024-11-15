# config/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv('KUCOIN_API_KEY')
    API_SECRET = os.getenv('KUCOIN_API_SECRET')
    API_PASSPHRASE = os.getenv('KUCOIN_API_PASSPHRASE')
    # Notification Configuration
    NOTIFICATIONS = {
        'email': {
            'enabled': bool(os.getenv('EMAIL_ENABLED', 'False')),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'to_email': os.getenv('EMAIL_TO')
        },
        'telegram': {
            'enabled': bool(os.getenv('TELEGRAM_ENABLED', 'False')),
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'chat_id': os.getenv('TELEGRAM_CHAT_ID')
        }
    }
    
    # Trading Configuration
    TRADING_PAIRS = os.getenv('TRADING_PAIRS', 'BTC-USDT,ETH-USDT').split(',')
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 100))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 2))
    TAKE_PROFIT_PERCENTAGE = float(os.getenv('TAKE_PROFIT_PERCENTAGE', 4))
    
    # Risk Management
    MAX_TRADES_PER_DAY = int(os.getenv('MAX_TRADES_PER_DAY', 10))
    MAX_POSITION_PERCENTAGE = float(os.getenv('MAX_POSITION_PERCENTAGE', 20))
    
    # Timeframes
    TRADING_TIMEFRAME = os.getenv('TRADING_TIMEFRAME', '15m')

    @staticmethod
    def validate_config():
        """Validate that all required configuration parameters are set"""
        required_vars = [
            'API_KEY',
            'API_SECRET',
            'API_PASSPHRASE'
        ]
        
        missing_vars = [var for var in required_vars if getattr(Config, var) is None]
        
        if missing_vars:
            raise ValueError(f"Missing required configuration variables: {', '.join(missing_vars)}")