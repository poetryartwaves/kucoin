# modules/interface/web_server.py

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import pandas as pd
import threading
import queue
import json

class WebInterface:
    def __init__(self, trading_engine):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.trading_engine = trading_engine
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.market_data_cache = {}
        self.alert_history = []
        self.update_queue = queue.Queue()
        
        # Monitoring thresholds
        self.price_alert_threshold = 0.02  # 2% price change
        self.volume_alert_threshold = 1.5   # 50% volume increase
        
        # Register routes and socket events
        self.register_routes()
        self.register_socket_events()
        
        # Start background tasks
        self.start_background_tasks()

    def register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', 
                                trading_pairs=self.trading_engine.trading_pairs)

        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'status': 'running' if self.trading_engine.is_running else 'stopped',
                'uptime': self.trading_engine.get_uptime(),
                'trades_today': self.trading_engine.daily_stats['trades'],
                'pnl_today': self.trading_engine.daily_stats['pnl'],
                'active_pairs': len(self.trading_engine.trading_pairs),
                'open_positions': len(self.trading_engine.position_manager.get_all_positions()),
                'last_update': datetime.now().isoformat()
            })

        @self.app.route('/api/trades')
        def get_trades():
            limit = request.args.get('limit', 50, type=int)
            return jsonify(self.trading_engine.trades_history[-limit:])

        @self.app.route('/api/performance')
        def get_performance():
            return jsonify(self.trading_engine.get_performance_metrics())

        @self.app.route('/api/positions')
        def get_positions():
            return jsonify(self.trading_engine.position_manager.get_all_positions())

        @self.app.route('/api/market-data')
        def get_market_data():
            return jsonify(self.market_data_cache)

        @self.app.route('/api/alerts')
        def get_alerts():
            limit = request.args.get('limit', 20, type=int)
            return jsonify(self.alert_history[-limit:])

        @self.app.route('/api/control/start', methods=['POST'])
        def start_trading():
            try:
                if not self.trading_engine.is_running:
                    self.trading_engine.start()
                    return jsonify({'status': 'success', 'message': 'Trading started'})
                return jsonify({'status': 'warning', 'message': 'Trading already running'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})

        @self.app.route('/api/control/stop', methods=['POST'])
        def stop_trading():
            try:
                if self.trading_engine.is_running:
                    self.trading_engine.stop()
                    return jsonify({'status': 'success', 'message': 'Trading stopped'})
                return jsonify({'status': 'warning', 'message': 'Trading already stopped'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})

        @self.app.route('/api/control/add-pair', methods=['POST'])
        def add_trading_pair():
            try:
                pair = request.json.get('pair')
                if pair and pair not in self.trading_engine.trading_pairs:
                    self.trading_engine.trading_pairs.append(pair)
                    return jsonify({'status': 'success', 'message': f'Added {pair}'})
                return jsonify({'status': 'warning', 'message': 'Invalid pair or already exists'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})

    def register_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            self.logger.info('Client connected')
            self.emit_update('status', {
                'status': 'running' if self.trading_engine.is_running else 'stopped',
                'uptime': self.trading_engine.get_uptime()
            })

        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.logger.info('Client disconnected')

    def start_background_tasks(self):
        """Start background monitoring tasks"""
        def update_processor():
            while True:
                try:
                    update = self.update_queue.get()
                    if update:
                        event_type, data = update
                        self.emit_update(event_type, data)
                except Exception as e:
                    self.logger.error(f"Error processing update: {str(e)}")

        threading.Thread(target=update_processor, daemon=True).start()

    def monitor_price_changes(self, symbol: str, current_price: float):
        """Monitor significant price changes"""
        if symbol in self.market_data_cache:
            last_price = self.market_data_cache[symbol]['price']
            price_change = abs(current_price - last_price) / last_price
            
            if price_change >= self.price_alert_threshold:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'PRICE_ALERT',
                    'symbol': symbol,
                    'message': f'Significant price change: {price_change:.2%}',
                    'data': {
                        'old_price': last_price,
                        'new_price': current_price,
                        'change_pct': price_change * 100
                    }
                }
                self.add_alert(alert)

    def monitor_volume_changes(self, symbol: str, current_volume: float):
        """Monitor significant volume changes"""
        if symbol in self.market_data_cache:
            last_volume = self.market_data_cache[symbol]['volume']
            volume_change = current_volume / last_volume if last_volume > 0 else 0
            
            if volume_change >= self.volume_alert_threshold:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'VOLUME_ALERT',
                    'symbol': symbol,
                    'message': f'Significant volume increase: {volume_change:.2%}',
                    'data': {
                        'old_volume': last_volume,
                        'new_volume': current_volume,
                        'change_pct': (volume_change - 1) * 100
                    }
                }
                self.add_alert(alert)

    def add_alert(self, alert: Dict[str, Any]):
        """Add alert to history and notify clients"""
        self.alert_history.append(alert)
        self.update_queue.put(('alert', alert))

    def update_market_data(self, symbol: str, data: Dict[str, Any]):
        """Update market data and check for significant changes"""
        try:
            # Monitor changes if we have previous data
            if symbol in self.market_data_cache:
                self.monitor_price_changes(symbol, data['current_price'])
                self.monitor_volume_changes(symbol, data.get('volume_24h', 0))

            # Update cache
            self.market_data_cache[symbol] = {
                'price': data['current_price'],
                'volume': data.get('volume_24h', 0),
                'timestamp': datetime.now().isoformat(),
                'signal': data.get('signal'),
                'indicators': {
                    'rsi': data.get('rsi'),
                    'macd': data.get('macd'),
                    'ema_fast': data.get('ema_fast'),
                    'ema_slow': data.get('ema_slow')
                }
            }

            # Queue update for clients
            self.update_queue.put(('market_data', {
                'symbol': symbol,
                'data': self.market_data_cache[symbol]
            }))

        except Exception as e:
            self.logger.error(f"Error updating market data: {str(e)}")

    def update_position(self, symbol: str, position: Dict[str, Any]):
        """Update position information"""
        try:
            self.update_queue.put(('position', {
                'symbol': symbol,
                'position': position
            }))
        except Exception as e:
            self.logger.error(f"Error updating position: {str(e)}")

    def log_trade(self, trade: Dict[str, Any]):
        """Log trade and notify clients"""
        try:
            self.update_queue.put(('trade', trade))
        except Exception as e:
            self.logger.error(f"Error logging trade: {str(e)}")

    def emit_update(self, event: str, data: Dict[str, Any]):
        """Emit update to connected clients"""
        try:
            self.socketio.emit(event, data)
        except Exception as e:
            self.logger.error(f"Error emitting update: {str(e)}")

    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """Run the web server"""
        try:
            self.socketio.run(self.app, host=host, port=port, debug=False)
        except Exception as e:
            self.logger.error(f"Error running web server: {str(e)}")