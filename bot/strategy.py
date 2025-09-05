"""
Toyota Corolla Trading Bot - Strategy Logic
Simple, reliable signal generation
Week 2: 5-factor confluence strategy implementation
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from bot.indicators import TechnicalIndicators
from config.settings import config

logger = logging.getLogger(__name__)

class StrategySignal:
    """Simple signal data structure"""
    def __init__(self, signal_type: str, strength: float, price: float, reasons: List[str]):
        self.signal_type = signal_type  # 'LONG', 'SHORT', 'EXIT', 'NO_SIGNAL'
        self.strength = strength        # 0.0 to 1.0
        self.price = price             # Signal price
        self.reasons = reasons         # List of reasons for signal
        self.timestamp = datetime.now()

class CorollaStrategy:
    """Toyota Corolla Strategy - Simple 5-factor confluence"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.market_data_1m = {'high': [], 'low': [], 'close': [], 'volume': []}
        self.market_data_15m = {'high': [], 'low': [], 'close': [], 'volume': []}
        
        # Strategy state
        self.last_signal = None
        self.momentum_window_active = False
        self.momentum_window_remaining = 0
        self.break_level = 0.0
        self.break_direction = ""
        
        logger.info("🎯 Toyota Corolla Strategy initialized")
    
    def update_market_data(self, candle_data: Dict, timeframe: str = "1m"):
        """Update market data with new candle"""
        try:
            if timeframe == "1m":
                data = self.market_data_1m
            elif timeframe == "15m":
                data = self.market_data_15m
            else:
                logger.warning(f"Unknown timeframe: {timeframe}")
                return
            
            # Add new candle data
            data['high'].append(float(candle_data['high']))
            data['low'].append(float(candle_data['low']))
            data['close'].append(float(candle_data['close']))
            data['volume'].append(int(candle_data.get('volume', 1000)))
            
            # Keep only last 200 candles for memory efficiency
            if len(data['close']) > 200:
                for key in data:
                    data[key] = data[key][-200:]
            
            logger.debug(f"Updated {timeframe} data: {len(data['close'])} candles")
            
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    def check_confluence_factors(self, indicators: Dict) -> Dict[str, bool]:
        """Check all 5 confluence factors for signal generation"""
        try:
            factors = {
                'white_dot': False,      # Squeeze exit (white dot)
                'sqzmom_color': False,   # Correct SQZMOM color
                'atf_1m_confirm': False, # 1m ATF confirms direction
                'atf_15m_confirm': False,# 15m ATF confirms direction  
                'break_strength': False  # Strong S/R break
            }
            
            squeeze_data = indicators.get('squeeze_mom', {})
            atf_1m = indicators.get('atf_1m', 0)
            atf_15m = indicators.get('atf_15m', 0)
            
            # Factor 1: White dot (squeeze exit)
            # This would require previous bar data - simplified for now
            factors['white_dot'] = not squeeze_data.get('in_squeeze', True)
            
            # Factor 2: SQZMOM color (momentum direction)
            momentum = squeeze_data.get('momentum', 0)
            if self.break_direction == "LONG":
                factors['sqzmom_color'] = momentum > 0  # Green/Lime bars
            elif self.break_direction == "SHORT":
                factors['sqzmom_color'] = momentum < 0  # Red bars
            
            # Factor 3: ATF 1m confirmation
            if self.break_direction == "LONG":
                factors['atf_1m_confirm'] = atf_1m >= 0  # Bullish or neutral
            elif self.break_direction == "SHORT":
                factors['atf_1m_confirm'] = atf_1m <= 0  # Bearish or neutral
            
            # Factor 4: ATF 15m confirmation (use 1m for now until we have 15m data)
            factors['atf_15m_confirm'] = factors['atf_1m_confirm']  # Simplified
            
            # Factor 5: Break strength
            current_price = indicators.get('current_price', 0)
            if self.break_level > 0 and current_price > 0:
                break_percent = abs(current_price - self.break_level) / self.break_level
                factors['break_strength'] = break_percent >= 0.001  # 0.1% minimum break
            
            confluence_count = sum(factors.values())
            logger.debug(f"Confluence factors: {confluence_count}/5 - {factors}")
            
            return factors
            
        except Exception as e:
            logger.error(f"Error checking confluence factors: {e}")
            return {}
    
    def detect_support_resistance_break(self, indicators: Dict) -> Optional[str]:
        """Detect if price has broken support or resistance"""
        try:
            current_price = indicators.get('current_price', 0)
            sr_levels = indicators.get('support_resistance', {})
            
            resistance_levels = sr_levels.get('resistance', [])
            support_levels = sr_levels.get('support', [])
            
            # Check resistance breaks (for LONG signals)
            for resistance in resistance_levels:
                if current_price > resistance * 1.001:  # 0.1% above resistance
                    self.break_level = resistance
                    self.break_direction = "LONG"
                    logger.info(f"🟢 Resistance break detected: {current_price} > {resistance}")
                    return "RESISTANCE_BREAK"
            
            # Check support breaks (for SHORT signals)  
            for support in support_levels:
                if current_price < support * 0.999:  # 0.1% below support
                    self.break_level = support
                    self.break_direction = "SHORT"
                    logger.info(f"🔴 Support break detected: {current_price} < {support}")
                    return "SUPPORT_BREAK"
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting S/R breaks: {e}")
            return None
    
    def generate_signal(self) -> Optional[StrategySignal]:
        """Generate trading signal based on current market conditions"""
        try:
            # Need minimum data
            if len(self.market_data_1m['close']) < 50:
                logger.debug("Insufficient data for signal generation")
                return StrategySignal("NO_SIGNAL", 0.0, 0.0, ["Insufficient data"])
            
            # Calculate indicators
            indicators = self.indicators.calculate_all_indicators(self.market_data_1m)
            if not indicators:
                return StrategySignal("NO_SIGNAL", 0.0, 0.0, ["Indicator calculation failed"])
            
            current_price = indicators.get('current_price', 0)
            
            # Step 1: Look for S/R breaks
            break_type = self.detect_support_resistance_break(indicators)
            
            if break_type and not self.momentum_window_active:
                # Start momentum window
                self.momentum_window_active = True
                self.momentum_window_remaining = config.MOMENTUM_WINDOW
                logger.info(f"🕐 Momentum window started: {self.momentum_window_remaining} candles remaining")
            
            # Step 2: If in momentum window, check for confluence
            if self.momentum_window_active:
                confluence_factors = self.check_confluence_factors(indicators)
                confluence_count = sum(confluence_factors.values())
                
                # Need at least 4 out of 5 factors
                if confluence_count >= 4:
                    signal_type = self.break_direction
                    reasons = [f"{k}: {v}" for k, v in confluence_factors.items() if v]
                    
                    # Calculate signal strength based on confluence
                    strength = confluence_count / 5.0
                    
                    logger.info(f"🚨 SIGNAL GENERATED: {signal_type} at {current_price} (strength: {strength:.2f})")
                    
                    # Reset momentum window
                    self.momentum_window_active = False
                    self.momentum_window_remaining = 0
                    
                    return StrategySignal(signal_type, strength, current_price, reasons)
                
                # Count down momentum window
                self.momentum_window_remaining -= 1
                logger.debug(f"Momentum window: {self.momentum_window_remaining} candles remaining, confluence: {confluence_count}/5")
                
                if self.momentum_window_remaining <= 0:
                    logger.info("⏰ Momentum window expired without signal")
                    self.momentum_window_active = False
                    self.break_level = 0.0
                    self.break_direction = ""
            
            return StrategySignal("NO_SIGNAL", 0.0, current_price, ["Waiting for setup"])
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return StrategySignal("NO_SIGNAL", 0.0, 0.0, [f"Error: {str(e)}"])
    
    def should_exit_position(self, current_position: float, current_price: float) -> Optional[StrategySignal]:
        """Check if we should exit current position"""
        try:
            if current_position == 0:
                return None
            
            # Calculate indicators for exit logic
            indicators = self.indicators.calculate_all_indicators(self.market_data_1m)
            if not indicators:
                return None
            
            atf_1m = indicators.get('atf_1m', 0)
            
            # ATF flip exit logic
            if current_position > 0 and atf_1m < 0:  # Long position, ATF turns bearish
                return StrategySignal("EXIT", 0.8, current_price, ["ATF flip bearish"])
            elif current_position < 0 and atf_1m > 0:  # Short position, ATF turns bullish
                return StrategySignal("EXIT", 0.8, current_price, ["ATF flip bullish"])
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get current strategy status"""
        return {
            'momentum_window_active': self.momentum_window_active,
            'momentum_window_remaining': self.momentum_window_remaining,
            'break_level': self.break_level,
            'break_direction': self.break_direction,
            'data_1m_bars': len(self.market_data_1m['close']),
            'data_15m_bars': len(self.market_data_15m['close']),
            'last_signal': self.last_signal.signal_type if self.last_signal else "None"
        }