"""
Toyota Corolla Bot Configuration
Simple, reliable configuration management
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Simple configuration class"""
    
    # IBKR Connection
    IBKR_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
    IBKR_PORT = int(os.getenv('IBKR_PORT', '7497'))  # TWS Paper Trading
    IBKR_CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '1'))
    
    # Demo Mode (for testing without TWS)
    DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'
    
    # Trading
    SYMBOL = 'NQ'  # E-mini Nasdaq futures
    POSITION_SIZE = 1  # Start small - 1 micro contract
    
    # Strategy Parameters (from your analysis)
    ATF_1M_MAIN = 6
    ATF_1M_SMOOTH = 14
    ATF_1M_SENS = 2.0
    ATF_15M_MAIN = 10
    ATF_15M_SMOOTH = 14
    ATF_15M_SENS = 2.0
    
    LUX_LEFT = 10
    LUX_RIGHT = 5
    
    SQZMOM_BB_LENGTH = 20
    SQZMOM_BB_MULT = 2.0
    SQZMOM_KC_LENGTH = 20
    SQZMOM_KC_MULT = 1.5
    
    MOMENTUM_WINDOW = 6  # 6-candle signal window
    
    # Risk Management
    STOP_LOSS_POINTS = 25.0  # NQ stop loss
    MAX_DAILY_LOSS = 500.0   # Max daily loss in $
    MAX_DAILY_TRADES = 10    # Max trades per day
    
    # Dashboard
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '5001'))  # Changed from 5000 due to macOS AirPlay
    DASHBOARD_HOST = '0.0.0.0'
    
    # Email Alerts (optional)
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASS = os.getenv('EMAIL_PASS', '')
    ALERT_TO = os.getenv('ALERT_TO', '')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/bot.log'
    TRADE_LOG = 'logs/trades.csv'

# Global config instance
config = Config()