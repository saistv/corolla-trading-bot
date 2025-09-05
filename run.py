"""
Toyota Corolla Trading Bot - Main Entry Point
Simple, reliable, gets the job done.
"""
import logging
import time
import threading
from datetime import datetime
from bot.ibkr_connection import IBKRConnection
from bot.strategy import CorollaStrategy
from dashboard.app import app, set_bot_instance
from config.settings import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CorollaTradingBot:
    """Main bot class - Keep it simple!"""
    
    def __init__(self):
        self.ibkr = IBKRConnection()
        self.strategy = CorollaStrategy()
        self.running = False
        self.start_time = datetime.now()
        
        # Trading state
        self.position = 0
        self.entry_price = 0.0
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.error_count = 0
        self.last_signal = "None"
        
        logger.info("🚗 Toyota Corolla Trading Bot initialized")
    
    def start(self):
        """Start the bot"""
        logger.info("🚀 Starting Toyota Corolla Trading Bot...")
        
        # Connect to IBKR (skip in demo mode)
        if not config.DEMO_MODE:
            if not self.ibkr.connect():
                logger.error("❌ Failed to connect to IBKR. Exiting.")
                return False
        else:
            logger.info("🎭 Running in DEMO MODE - No IBKR connection needed")
        
        self.running = True
        
        # Start dashboard in separate thread
        dashboard_thread = threading.Thread(target=self._start_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        # Main trading loop
        self._main_loop()
        
        return True
    
    def stop(self):
        """Stop the bot"""
        logger.info("🛑 Stopping Toyota Corolla Trading Bot...")
        self.running = False
        self.ibkr.disconnect()
    
    def _start_dashboard(self):
        """Start the Flask dashboard"""
        set_bot_instance(self)
        app.run(
            host=config.DASHBOARD_HOST,
            port=config.DASHBOARD_PORT,
            debug=False,
            use_reloader=False
        )
    
    def _main_loop(self):
        """Main bot loop - Week 1: Just get data flowing"""
        logger.info("📊 Starting main loop...")
        
        while self.running:
            try:
                # Week 2: Data collection + indicator calculations + signal generation
                if config.DEMO_MODE:
                    # Demo data for testing
                    import random
                    current_price = 18500 + random.randint(-100, 100)
                    current_position = 0
                    
                    # Generate demo candle data
                    demo_candle = {
                        'high': current_price + random.randint(0, 10),
                        'low': current_price - random.randint(0, 10), 
                        'close': current_price,
                        'volume': random.randint(800, 1200)
                    }
                else:
                    current_price = self.ibkr.get_current_price()
                    current_position = self.ibkr.get_position()
                    
                    # Get historical bars for real candle data
                    bars = self.ibkr.get_historical_data("1 D", "1 min")
                    if bars:
                        latest_bar = bars[-1]
                        demo_candle = {
                            'high': latest_bar.high,
                            'low': latest_bar.low,
                            'close': latest_bar.close, 
                            'volume': latest_bar.volume
                        }
                    else:
                        demo_candle = {
                            'high': current_price + 5,
                            'low': current_price - 5,
                            'close': current_price,
                            'volume': 1000
                        }
                
                if current_price > 0:
                    logger.info(f"NQ Price: {current_price}, Position: {current_position}")
                
                # Update internal state
                self.position = current_position
                
                # Week 2: Update strategy with market data
                self.strategy.update_market_data(demo_candle, "1m")
                
                # Week 2: Generate trading signals  
                signal = self.strategy.generate_signal()
                if signal and signal.signal_type != "NO_SIGNAL":
                    logger.info(f"🚨 SIGNAL: {signal.signal_type} at {signal.price} (strength: {signal.strength:.2f})")
                    self.last_signal = f"{signal.signal_type} @ {signal.price:.0f}"
                    
                    # Week 4+: Execute trades based on signals
                
                # Check for exit signals
                exit_signal = self.strategy.should_exit_position(self.position, current_price)
                if exit_signal:
                    logger.info(f"🚪 EXIT: {exit_signal.reasons}")
                    self.last_signal = f"EXIT @ {exit_signal.price:.0f}"
                
                # Sleep for 60 seconds (1-minute bars)
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("👋 Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                self.error_count += 1
                time.sleep(30)  # Wait before retrying
        
        self.stop()
    
    def get_status(self) -> dict:
        """Get current bot status for dashboard"""
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        current_price = self.ibkr.get_current_price()
        unrealized_pnl = 0.0
        
        if self.position != 0 and self.entry_price > 0:
            # Calculate unrealized P&L (simplified)
            if self.position > 0:  # Long position
                unrealized_pnl = (current_price - self.entry_price) * self.position * 20  # $20 per point for NQ
            else:  # Short position
                unrealized_pnl = (self.entry_price - current_price) * abs(self.position) * 20
        
        return {
            'status': 'Running' if self.running else 'Stopped',
            'uptime': uptime_str,
            'trades_today': self.trades_today,
            'daily_pnl': self.daily_pnl,
            'win_rate': 0.0,  # Calculate later
            'position': self.position,
            'entry_price': self.entry_price,
            'current_price': current_price,
            'unrealized_pnl': unrealized_pnl,
            'ibkr_connected': self.ibkr.connected,
            'data_feed_ok': current_price > 0,
            'last_signal': self.last_signal,
            'error_count': self.error_count
        }

def main():
    """Main entry point"""
    logger.info("🚗 Toyota Corolla Trading Bot - Starting Up...")
    logger.info(f"📍 Dashboard will be available at: http://localhost:{config.DASHBOARD_PORT}")
    
    bot = CorollaTradingBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
    finally:
        bot.stop()
        logger.info("✅ Bot stopped cleanly")

if __name__ == "__main__":
    main()