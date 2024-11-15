# test_connection.py
from kucoin.client import Client
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_connection():
    try:
        # Replace with your actual API credentials from main Kucoin platform
        api_key = '6736611755222800016ad71f'
        api_secret = 'f518a24e-efe5-4a8d-8ea6-51cde3f5326e'
        api_passphrase = '0913@Safi@Yazd'
        
        # Initialize client (sandbox=False for main platform)
        client = Client(
            api_key,
            api_secret,
            api_passphrase,
            sandbox=False  # Using main platform
        )

        # Test API connection
        currencies = client.get_currencies()
        logging.info("Successfully connected to Kucoin API!")
        logging.info(f"Retrieved {len(currencies)} currencies")
        
        # Get account information
        accounts = client.get_accounts()
        logging.info("Account Information:")
        logging.info(accounts)
        
        # Get BTC-USDT ticker
        ticker = client.get_ticker('BTC-USDT')
        logging.info(f"BTC-USDT Market Data: {ticker}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection()