# modules/api_handler/error_handler.py

import logging
from typing import Dict, Any
from requests.exceptions import RequestException
from kucoin.exceptions import KucoinAPIException

class KucoinErrorHandler:
    @staticmethod
    def handle_api_error(error: Exception) -> Dict[str, Any]:
        """
        Handle different types of API errors and return appropriate response
        """
        if isinstance(error, KucoinAPIException):
            error_message = f"Kucoin API Error: {str(error)}"
            error_code = getattr(error, 'code', 'unknown')
            logging.error(f"{error_message} (Code: {error_code})")
            return {
                'success': False,
                'error': error_message,
                'code': error_code
            }
        
        elif isinstance(error, RequestException):
            error_message = f"Network Error: {str(error)}"
            logging.error(error_message)
            return {
                'success': False,
                'error': error_message,
                'code': 'network_error'
            }
        
        else:
            error_message = f"Unexpected Error: {str(error)}"
            logging.error(error_message)
            return {
                'success': False,
                'error': error_message,
                'code': 'unexpected_error'
            }

    @staticmethod
    def check_response(response: Dict[str, Any]) -> bool:
        """
        Check if the API response is valid
        """
        if not response:
            logging.error("Empty response received")
            return False
        
        if isinstance(response, dict) and response.get('code') != "200000":
            logging.error(f"API Error: {response.get('msg', 'Unknown error')}")
            return False
            
        return True