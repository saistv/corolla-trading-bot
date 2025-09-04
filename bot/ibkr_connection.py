"""
IBKR Connection Module
Simple, reliable connection to Interactive Brokers
"""
import logging
from datetime import datetime
from typing import List, Optional
from ib_insync import *
from config.settings import config

logger = logging.getLogger(__name__)

class IBKRConnection:
    """Simple IBKR connection wrapper"""
    
    def __init__(self):
        self.ib = IB()
        self.connected = False
        self.contract = None
        self.last_price = 0.0
        
    def connect(self) -> bool:
        """Connect to IBKR TWS/Gateway"""
        try:
            logger.info(f"Connecting to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}")
            self.ib.connect(
                host=config.IBKR_HOST,
                port=config.IBKR_PORT, 
                clientId=config.IBKR_CLIENT_ID,
                timeout=10
            )
            
            # Set up NQ contract
            self.contract = Future(
                symbol=config.SYMBOL,
                exchange='CME',
                currency='USD'
            )
            
            # Qualify the contract
            self.ib.qualifyContracts(self.contract)
            logger.info(f"Qualified contract: {self.contract}")
            
            self.connected = True
            logger.info("✅ Connected to IBKR successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to IBKR: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")
    
    def get_current_price(self) -> float:
        """Get current market price for NQ"""
        if not self.connected:
            return 0.0
            
        try:
            ticker = self.ib.reqMktData(self.contract)
            self.ib.sleep(1)  # Wait for price update
            
            if ticker.last and ticker.last > 0:
                self.last_price = ticker.last
                return ticker.last
            elif ticker.close and ticker.close > 0:
                self.last_price = ticker.close
                return ticker.close
            else:
                return self.last_price
                
        except Exception as e:
            logger.error(f"Error getting price: {e}")
            return self.last_price
    
    def get_historical_data(self, duration: str = "1 D", bar_size: str = "1 min") -> List:
        """Get historical bars for NQ"""
        if not self.connected:
            return []
            
        try:
            bars = self.ib.reqHistoricalData(
                contract=self.contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,  # Regular trading hours only
                formatDate=1
            )
            
            logger.info(f"Retrieved {len(bars)} historical bars")
            return bars
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []
    
    def get_position(self) -> float:
        """Get current NQ position"""
        if not self.connected:
            return 0.0
            
        try:
            positions = self.ib.positions()
            for pos in positions:
                if pos.contract.symbol == config.SYMBOL:
                    return pos.position
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return 0.0
    
    def place_market_order(self, action: str, quantity: int = 1) -> bool:
        """Place market order (BUY/SELL)"""
        if not self.connected:
            logger.error("Not connected to IBKR")
            return False
            
        try:
            order = MarketOrder(
                action=action,  # 'BUY' or 'SELL'
                totalQuantity=quantity
            )
            
            trade = self.ib.placeOrder(self.contract, order)
            logger.info(f"Placed {action} order for {quantity} {config.SYMBOL}")
            
            # Wait a bit for order to process
            self.ib.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    def place_stop_order(self, action: str, stop_price: float, quantity: int = 1) -> bool:
        """Place stop loss order"""
        if not self.connected:
            return False
            
        try:
            order = StopOrder(
                action=action,
                totalQuantity=quantity,
                stopPrice=stop_price
            )
            
            trade = self.ib.placeOrder(self.contract, order)
            logger.info(f"Placed stop order: {action} {quantity} @ {stop_price}")
            return True
            
        except Exception as e:
            logger.error(f"Error placing stop order: {e}")
            return False
    
    def health_check(self) -> dict:
        """Simple health check"""
        return {
            'connected': self.connected,
            'last_price': self.last_price,
            'timestamp': datetime.now().isoformat()
        }