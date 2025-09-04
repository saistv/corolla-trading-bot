"""
Toyota Corolla Trading Bot Dashboard
Simple Flask web interface for monitoring
"""
from flask import Flask, jsonify, render_template_string
from datetime import datetime
import sys
import os

# Add parent directory to path to import bot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config

app = Flask(__name__)

# Global bot instance (will be set by main app)
bot = None

def set_bot_instance(bot_instance):
    """Set the bot instance for the dashboard to monitor"""
    global bot
    bot = bot_instance

@app.route('/')
def dashboard():
    """Simple HTML dashboard"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚗 Corolla Bot Status</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body { 
                font-family: monospace; 
                padding: 20px; 
                background-color: #f0f0f0;
            }
            .status-box { 
                border: 2px solid #333; 
                padding: 15px; 
                margin: 10px 0; 
                background-color: white;
            }
            .green { border-color: green; }
            .red { border-color: red; }
            .yellow { border-color: orange; }
            h1 { color: #333; }
            h2 { color: #666; }
        </style>
    </head>
    <body>
        <h1>🚗 Toyota Corolla Trading Bot</h1>
        <p><em>Simple, reliable, gets the job done.</em></p>
        
        <div id="status" class="status-box">Loading...</div>
        
        <h2>📊 Today's Performance</h2>
        <div id="trades" class="status-box">Loading...</div>
        
        <h2>📈 Current Position</h2>
        <div id="position" class="status-box">Loading...</div>
        
        <h2>🔌 System Health</h2>
        <div id="health" class="status-box">Loading...</div>
        
        <script>
            function updateDashboard() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        // Status
                        const statusDiv = document.getElementById('status');
                        statusDiv.innerHTML = 
                            `<strong>Status:</strong> ${data.status}<br>
                             <strong>Uptime:</strong> ${data.uptime}<br>
                             <strong>Last Update:</strong> ${data.last_update}`;
                        statusDiv.className = 'status-box ' + (data.status === 'Running' ? 'green' : 'red');
                        
                        // Trades
                        document.getElementById('trades').innerHTML = 
                            `<strong>Trades Today:</strong> ${data.trades_today}<br>
                             <strong>Daily P&L:</strong> $${data.daily_pnl}<br>
                             <strong>Win Rate:</strong> ${data.win_rate}%`;
                        
                        // Position
                        const posDiv = document.getElementById('position');
                        posDiv.innerHTML = 
                            `<strong>Position:</strong> ${data.position}<br>
                             <strong>Entry Price:</strong> ${data.entry_price}<br>
                             <strong>Current Price:</strong> ${data.current_price}<br>
                             <strong>Unrealized P&L:</strong> $${data.unrealized_pnl}`;
                        posDiv.className = 'status-box ' + (data.position == 0 ? 'yellow' : 'green');
                        
                        // Health
                        document.getElementById('health').innerHTML = 
                            `<strong>IBKR Connected:</strong> ${data.ibkr_connected ? '✅' : '❌'}<br>
                             <strong>Data Feed:</strong> ${data.data_feed_ok ? '✅' : '❌'}<br>
                             <strong>Last Signal:</strong> ${data.last_signal}<br>
                             <strong>Errors (24h):</strong> ${data.error_count}`;
                    })
                    .catch(error => {
                        console.error('Dashboard update failed:', error);
                        document.getElementById('status').innerHTML = '❌ Dashboard connection failed';
                        document.getElementById('status').className = 'status-box red';
                    });
            }
            
            // Update every 5 seconds
            updateDashboard();
            setInterval(updateDashboard, 5000);
        </script>
    </body>
    </html>
    ''')

@app.route('/api/status')
def status():
    """API endpoint for bot status"""
    if bot is None:
        return jsonify({
            'status': 'Not Started',
            'uptime': '0:00:00',
            'last_update': datetime.now().isoformat(),
            'trades_today': 0,
            'daily_pnl': 0.0,
            'win_rate': 0.0,
            'position': 0,
            'entry_price': 0.0,
            'current_price': 0.0,
            'unrealized_pnl': 0.0,
            'ibkr_connected': False,
            'data_feed_ok': False,
            'last_signal': 'None',
            'error_count': 0
        })
    
    try:
        # Get status from bot instance
        bot_status = bot.get_status()
        
        return jsonify({
            'status': bot_status.get('status', 'Unknown'),
            'uptime': bot_status.get('uptime', '0:00:00'),
            'last_update': datetime.now().isoformat(),
            'trades_today': bot_status.get('trades_today', 0),
            'daily_pnl': bot_status.get('daily_pnl', 0.0),
            'win_rate': bot_status.get('win_rate', 0.0),
            'position': bot_status.get('position', 0),
            'entry_price': bot_status.get('entry_price', 0.0),
            'current_price': bot_status.get('current_price', 0.0),
            'unrealized_pnl': bot_status.get('unrealized_pnl', 0.0),
            'ibkr_connected': bot_status.get('ibkr_connected', False),
            'data_feed_ok': bot_status.get('data_feed_ok', False),
            'last_signal': bot_status.get('last_signal', 'None'),
            'error_count': bot_status.get('error_count', 0)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Dashboard error: {str(e)}',
            'status': 'Error',
            'last_update': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Run dashboard standalone for testing
    app.run(
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=True
    )