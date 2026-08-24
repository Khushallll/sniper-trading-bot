"""Detect profitable trading opportunities"""

import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger
from src.analysis.indicators import TechnicalIndicators


@dataclass
class TradingOpportunity:
    """Represents a detected trading opportunity"""
    symbol: str
    timestamp: datetime
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence_score: float
    signal_type: str  # 'bullish' or 'bearish'
    indicators: Dict[str, float]
    reasoning: str


class OpportunityDetector:
    """Detects trading opportunities using technical analysis"""

    def __init__(self, config: Dict):
        """
        Initialize opportunity detector
        
        Args:
            config: Configuration dictionary with detection parameters
        """
        self.config = config
        self.indicators = TechnicalIndicators()
        logger.info("Initialized opportunity detector")

    def detect_opportunities(self, ohlcv_data: pd.DataFrame, 
                           symbol: str) -> List[TradingOpportunity]:
        """
        Detect trading opportunities in price data
        
        Args:
            ohlcv_data: OHLCV DataFrame
            symbol: Trading pair symbol
            
        Returns:
            List of detected opportunities
        """
        opportunities = []
        
        # Calculate technical indicators
        indicators = self._calculate_indicators(ohlcv_data)
        
        # Check for bullish opportunities
        if self._check_bullish_signals(ohlcv_data, indicators):
            opp = self._create_opportunity(
                ohlcv_data, indicators, symbol, 'bullish'
            )
            if opp:
                opportunities.append(opp)
        
        # Check for bearish opportunities
        if self._check_bearish_signals(ohlcv_data, indicators):
            opp = self._create_opportunity(
                ohlcv_data, indicators, symbol, 'bearish'
            )
            if opp:
                opportunities.append(opp)
        
        return opportunities

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate all technical indicators
        
        Args:
            df: OHLCV DataFrame
            
        Returns:
            Dictionary of indicators
        """
        indicators = {}
        
        # RSI
        indicators['rsi'] = self.indicators.calculate_rsi(df['close'])
        
        # MACD
        macd, signal, hist = self.indicators.calculate_macd(df['close'])
        indicators['macd'] = macd
        indicators['macd_signal'] = signal
        indicators['macd_hist'] = hist
        
        # Bollinger Bands
        upper, middle, lower = self.indicators.calculate_bollinger_bands(df['close'])
        indicators['bb_upper'] = upper
        indicators['bb_middle'] = middle
        indicators['bb_lower'] = lower
        
        # ATR
        indicators['atr'] = self.indicators.calculate_atr(
            df['high'], df['low'], df['close']
        )
        
        # Volume SMA
        indicators['volume_sma'] = self.indicators.calculate_volume_sma(df['volume'])
        
        # OBV
        indicators['obv'] = self.indicators.calculate_obv(df['close'], df['volume'])
        
        return indicators

    def _check_bullish_signals(self, df: pd.DataFrame, 
                               indicators: Dict[str, pd.Series]) -> bool:
        """
        Check for bullish signals
        
        Args:
            df: OHLCV DataFrame
            indicators: Technical indicators dictionary
            
        Returns:
            True if bullish signals are present
        """
        latest_idx = len(df) - 1
        
        rsi = indicators['rsi'].iloc[latest_idx]
        macd = indicators['macd'].iloc[latest_idx]
        macd_signal = indicators['macd_signal'].iloc[latest_idx]
        macd_hist = indicators['macd_hist'].iloc[latest_idx]
        close = df['close'].iloc[latest_idx]
        bb_lower = indicators['bb_lower'].iloc[latest_idx]
        volume = df['volume'].iloc[latest_idx]
        volume_sma = indicators['volume_sma'].iloc[latest_idx]
        
        # Bullish conditions
        rsi_bullish = (rsi > 30) and (rsi < 70)  # Not oversold
        macd_bullish = (macd > macd_signal) and (macd_hist > 0)  # MACD above signal
        price_bullish = close > bb_lower  # Price above lower band
        volume_bullish = volume > volume_sma  # Above average volume
        
        return rsi_bullish and macd_bullish and price_bullish and volume_bullish

    def _check_bearish_signals(self, df: pd.DataFrame, 
                               indicators: Dict[str, pd.Series]) -> bool:
        """
        Check for bearish signals
        
        Args:
            df: OHLCV DataFrame
            indicators: Technical indicators dictionary
            
        Returns:
            True if bearish signals are present
        """
        latest_idx = len(df) - 1
        
        rsi = indicators['rsi'].iloc[latest_idx]
        macd = indicators['macd'].iloc[latest_idx]
        macd_signal = indicators['macd_signal'].iloc[latest_idx]
        macd_hist = indicators['macd_hist'].iloc[latest_idx]
        close = df['close'].iloc[latest_idx]
        bb_upper = indicators['bb_upper'].iloc[latest_idx]
        volume = df['volume'].iloc[latest_idx]
        volume_sma = indicators['volume_sma'].iloc[latest_idx]
        
        # Bearish conditions
        rsi_bearish = (rsi > 30) and (rsi < 70)  # Not overbought
        macd_bearish = (macd < macd_signal) and (macd_hist < 0)  # MACD below signal
        price_bearish = close < bb_upper  # Price below upper band
        volume_bearish = volume > volume_sma  # Above average volume
        
        return rsi_bearish and macd_bearish and price_bearish and volume_bearish

    def _create_opportunity(self, df: pd.DataFrame, indicators: Dict[str, pd.Series],
                          symbol: str, signal_type: str) -> Optional[TradingOpportunity]:
        """
        Create opportunity object with risk/reward parameters
        
        Args:
            df: OHLCV DataFrame
            indicators: Technical indicators
            symbol: Trading pair
            signal_type: 'bullish' or 'bearish'
            
        Returns:
            TradingOpportunity or None
        """
        latest_idx = len(df) - 1
        entry_price = df['close'].iloc[latest_idx]
        atr = indicators['atr'].iloc[latest_idx]
        rsi = indicators['rsi'].iloc[latest_idx]
        
        if signal_type == 'bullish':
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 3.0)
        else:  # bearish
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 3.0)
        
        # Calculate confidence score (0-1)
        confidence = min(abs(rsi - 50) / 50 * 0.5 + 0.5, 1.0)
        
        opportunity = TradingOpportunity(
            symbol=symbol,
            timestamp=df.index[-1],
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence_score=confidence,
            signal_type=signal_type,
            indicators={
                'rsi': float(rsi),
                'macd': float(indicators['macd'].iloc[latest_idx]),
                'atr': float(atr)
            },
            reasoning=f"{signal_type.capitalize()} signal with RSI at {rsi:.2f}"
        )
        
        return opportunity
