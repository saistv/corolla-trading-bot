"""
Toyota Corolla Trading Bot - Technical Indicators
Simple, manual calculations without TA-Lib dependency
Week 2: ATF, SQZMOM, and LuxAlgo S/R indicators
"""
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from config.settings import config

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Simple technical indicator calculations"""
    
    def __init__(self):
        logger.info("🔧 Technical indicators module initialized")
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
            
        # EMA calculation
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
            
        return ema
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(highs) < 2 or len(lows) < 2 or len(closes) < 2:
            return 0.0
            
        true_ranges = []
        
        for i in range(1, len(highs)):
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            true_ranges.append(max(tr1, tr2, tr3))
        
        if len(true_ranges) < period:
            return sum(true_ranges) / len(true_ranges)
        
        return sum(true_ranges[-period:]) / period
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, multiplier: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (Upper, Middle, Lower)"""
        if len(prices) < period:
            return 0.0, 0.0, 0.0
            
        sma = self.calculate_sma(prices, period)
        
        # Calculate standard deviation
        recent_prices = prices[-period:]
        variance = sum([(price - sma) ** 2 for price in recent_prices]) / period
        std_dev = variance ** 0.5
        
        upper = sma + (std_dev * multiplier)
        lower = sma - (std_dev * multiplier)
        
        return upper, sma, lower
    
    def calculate_keltner_channels(self, highs: List[float], lows: List[float], closes: List[float], 
                                  period: int = 20, multiplier: float = 1.5) -> Tuple[float, float, float]:
        """Calculate Keltner Channels (Upper, Middle, Lower)"""
        if len(closes) < period:
            return 0.0, 0.0, 0.0
            
        # Middle line is EMA of close
        middle = self.calculate_ema(closes, period)
        
        # ATR for channel width
        atr = self.calculate_atr(highs, lows, closes, period)
        
        upper = middle + (atr * multiplier)
        lower = middle - (atr * multiplier)
        
        return upper, middle, lower
    
    def calculate_squeeze_mom(self, highs: List[float], lows: List[float], closes: List[float]) -> Dict[str, float]:
        """Calculate Squeeze Momentum indicator"""
        try:
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(
                closes, config.SQZMOM_BB_LENGTH, config.SQZMOM_BB_MULT
            )
            
            # Keltner Channels  
            kc_upper, kc_middle, kc_lower = self.calculate_keltner_channels(
                highs, lows, closes, config.SQZMOM_KC_LENGTH, config.SQZMOM_KC_MULT
            )
            
            # Squeeze detection: BB inside KC
            in_squeeze = (bb_upper < kc_upper) and (bb_lower > kc_lower)
            
            # Momentum calculation (simplified)
            if len(closes) >= 20:
                highest = max(highs[-20:])
                lowest = min(lows[-20:])
                close = closes[-1]
                
                # Normalize price position
                if highest != lowest:
                    momentum = ((close - (highest + lowest) / 2) + (close - self.calculate_sma(closes, 20))) / 2
                else:
                    momentum = 0.0
            else:
                momentum = 0.0
            
            return {
                'in_squeeze': in_squeeze,
                'momentum': momentum,
                'bb_upper': bb_upper,
                'bb_lower': bb_lower,
                'kc_upper': kc_upper,
                'kc_lower': kc_lower,
                'squeeze_exit': False  # Will be determined by comparing with previous bar
            }
            
        except Exception as e:
            logger.error(f"Error calculating Squeeze Momentum: {e}")
            return {
                'in_squeeze': False,
                'momentum': 0.0,
                'bb_upper': 0.0,
                'bb_lower': 0.0,
                'kc_upper': 0.0,
                'kc_lower': 0.0,
                'squeeze_exit': False
            }
    
    def calculate_atf(self, highs: List[float], lows: List[float], closes: List[float], 
                     main: int, smooth: int, sens: float) -> float:
        """Calculate Adaptive Trend Flow (ATF) - Simplified version"""
        try:
            if len(closes) < max(main, smooth):
                return 0.0
            
            # Calculate price momentum
            price_change = closes[-1] - closes[-main] if len(closes) >= main else 0.0
            
            # Smooth with EMA
            if len(closes) >= smooth:
                smoothed = self.calculate_ema(closes, smooth)
                current_price = closes[-1]
                
                # ATF signal: +1 for bullish, -1 for bearish, 0 for neutral
                if current_price > smoothed + sens:
                    return 1.0  # Bullish
                elif current_price < smoothed - sens:
                    return -1.0  # Bearish
                else:
                    return 0.0  # Neutral
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating ATF: {e}")
            return 0.0
    
    def calculate_atf_1m(self, highs: List[float], lows: List[float], closes: List[float]) -> float:
        """Calculate 1-minute ATF signal"""
        return self.calculate_atf(
            highs, lows, closes,
            config.ATF_1M_MAIN,
            config.ATF_1M_SMOOTH, 
            config.ATF_1M_SENS
        )
    
    def calculate_atf_15m(self, highs: List[float], lows: List[float], closes: List[float]) -> float:
        """Calculate 15-minute ATF signal"""
        return self.calculate_atf(
            highs, lows, closes,
            config.ATF_15M_MAIN,
            config.ATF_15M_SMOOTH,
            config.ATF_15M_SENS
        )
    
    def find_support_resistance(self, highs: List[float], lows: List[float], 
                               left_bars: int = 10, right_bars: int = 5) -> Dict[str, List[float]]:
        """Find support and resistance levels (LuxAlgo style)"""
        try:
            if len(highs) < left_bars + right_bars + 1:
                return {'support': [], 'resistance': []}
            
            supports = []
            resistances = []
            
            # Look for pivot points
            for i in range(left_bars, len(lows) - right_bars):
                # Check for support (pivot low)
                is_support = True
                current_low = lows[i]
                
                # Check left bars
                for j in range(i - left_bars, i):
                    if lows[j] <= current_low:
                        is_support = False
                        break
                
                # Check right bars
                if is_support:
                    for j in range(i + 1, i + right_bars + 1):
                        if lows[j] <= current_low:
                            is_support = False
                            break
                
                if is_support:
                    supports.append(current_low)
                
                # Check for resistance (pivot high)
                is_resistance = True
                current_high = highs[i]
                
                # Check left bars
                for j in range(i - left_bars, i):
                    if highs[j] >= current_high:
                        is_resistance = False
                        break
                
                # Check right bars  
                if is_resistance:
                    for j in range(i + 1, i + right_bars + 1):
                        if highs[j] >= current_high:
                            is_resistance = False
                            break
                
                if is_resistance:
                    resistances.append(current_high)
            
            # Keep only most recent levels
            supports = supports[-5:] if supports else []
            resistances = resistances[-5:] if resistances else []
            
            logger.debug(f"Found {len(supports)} support and {len(resistances)} resistance levels")
            
            return {
                'support': supports,
                'resistance': resistances
            }
            
        except Exception as e:
            logger.error(f"Error finding support/resistance: {e}")
            return {'support': [], 'resistance': []}
    
    def calculate_all_indicators(self, market_data: Dict[str, List]) -> Dict[str, any]:
        """Calculate all indicators for current market data"""
        try:
            if not market_data or 'close' not in market_data:
                return {}
            
            highs = market_data.get('high', [])
            lows = market_data.get('low', [])
            closes = market_data.get('close', [])
            
            if len(closes) < 20:  # Need minimum data
                logger.warning("Insufficient data for indicator calculations")
                return {}
            
            # Calculate all indicators
            indicators = {
                'atf_1m': self.calculate_atf_1m(highs, lows, closes),
                'atf_15m': self.calculate_atf_15m(highs, lows, closes),  # Will use 15m data when available
                'squeeze_mom': self.calculate_squeeze_mom(highs, lows, closes),
                'support_resistance': self.find_support_resistance(highs, lows, config.LUX_LEFT, config.LUX_RIGHT),
                'current_price': closes[-1],
                'sma_200': self.calculate_sma(closes, 200) if len(closes) >= 200 else 0.0,
            }
            
            logger.debug(f"Calculated indicators: ATF_1m={indicators['atf_1m']}, Squeeze={indicators['squeeze_mom']['in_squeeze']}")
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return {}