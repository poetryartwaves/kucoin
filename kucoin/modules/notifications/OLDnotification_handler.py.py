# C:\kucoin\modules\notifications\notification_handler.py

import logging
import requests
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any
from config.config import Config

class NotificationHandler:
    """Handler for sending notifications via different channels"""
    
    def __init__(self):
        """Initialize notification handler with config settings"""
        self.logger = logging.getLogger(__name__)
        
        # Email settings
        self.email_enabled = Config.NOTIFICATIONS['email']['enabled']
        self.smtp_server = Config.NOTIFICATIONS['email']['smtp_server']
        self.smtp_port = Config.NOTIFICATIONS['email']['smtp_port']
        self.email_username = Config.NOTIFICATIONS['email']['username']
        self.email_password = Config.NOTIFICATIONS['email']['password']
        self.email_to = Config.NOTIFICATIONS['email']['to_email']
        
        # Telegram settings
        self.telegram_enabled = Config.NOTIFICATIONS['telegram']['enabled']
        self.telegram_bot_token = Config.NOTIFICATIONS['telegram']['bot_token']
        self.telegram_chat_id = Config.NOTIFICATIONS['telegram']['chat_id']

    def send_telegram_message(self, message: str) -> bool:
        """Send message via Telegram"""
        try:
            if not self.telegram_enabled:
                self.logger.info("Telegram notifications are disabled")
                return False

            if not all([self.telegram_bot_token, self.telegram_chat_id]):
                self.logger.warning("Telegram credentials not configured")
                return False

            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.logger.info("Telegram message sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send Telegram message: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False

    def send_email(self, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            if not self.email_enabled:
                self.logger.info("Email notifications are disabled")
                return False

            if not all([self.email_username, self.email_password, self.email_to]):
                self.logger.warning("Email credentials not configured")
                return False

            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.email_username
            msg['To'] = self.email_to

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()

            self.logger.info("Email sent successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False

    def notify(self, message: str, level: str = 'info') -> None:
        """Send notification through all enabled channels"""
        try:
            # Log the message
            self.logger.info(f"Notification ({level}): {message}")

            # Send via Telegram if enabled
            if self.telegram_enabled:
                self.send_telegram_message(message)
            
            # Send via email if enabled
            if self.email_enabled:
                subject = f"Trading Bot Alert - {level.upper()}"
                self.send_email(subject, message)

        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")

    def notify_trade(self, trade: Dict[str, Any]) -> None:
        """Send trade notification"""
        try:
            emoji = "🟢" if trade['type'] == 'BUY' else "🔴"
            message = (
                f"{emoji} Trade Alert\n"
                f"Type: {trade['type']}\n"
                f"Symbol: {trade['symbol']}\n"
                f"Price: ${trade['price']:,.2f}\n"
                f"Size: {trade['size']:.8f}"
            )
            
            if trade.get('pnl') is not None:
                pnl_emoji = "✅" if trade['pnl'] > 0 else "❌"
                message += f"\nPnL: {pnl_emoji} ${trade['pnl']:,.2f}"

            self.notify(message, level='important')

        except Exception as e:
            self.logger.error(f"Error sending trade notification: {str(e)}")

    def notify_error(self, error_message: str) -> None:
        """Send error notification"""
        try:
            message = f"⚠️ Error Alert\n{error_message}"
            self.notify(message, level='critical')

        except Exception as e:
            self.logger.error(f"Error sending error notification: {str(e)}")

    def notify_performance(self, metrics: Dict[str, Any]) -> None:
        """Send performance notification"""
        try:
            message = (
                f"📊 Performance Update\n"
                f"Total Trades: {metrics['total_trades']}\n"
                f"Win Rate: {metrics['win_rate']:.2f}%\n"
                f"Daily PnL: ${metrics['daily_pnl']:,.2f}\n"
                f"Total PnL: ${metrics['total_pnl']:,.2f}\n"
            )

            self.notify(message, level='important')

        except Exception as e:
            self.logger.error(f"Error sending performance notification: {str(e)}")