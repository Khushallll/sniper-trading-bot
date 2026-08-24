"""Tests for technical indicators"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.indicators import TechnicalIndicators


@pytest.fixture
def sample_data():
    """Create sample price data for testing"""
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')
    prices = np.random.uniform(100, 110, 100)
    return pd.Series(prices, index=dates)


class TestTechnicalIndicators:
    """Test technical indicator calculations"""

    def test_rsi_calculation(self, sample_data):
        """Test RSI calculation"""
        rsi = TechnicalIndicators.calculate_rsi(sample_data)
        
        # RSI should be between 0 and 100
        assert rsi.dropna().min() >= 0
        assert rsi.dropna().max() <= 100
        # Should have NaN values for initial period
        assert rsi.isna().sum() > 0

    def test_macd_calculation(self, sample_data):
        """Test MACD calculation"""
        macd, signal, hist = TechnicalIndicators.calculate_macd(sample_data)
        
        # All should be Series
        assert isinstance(macd, pd.Series)
        assert isinstance(signal, pd.Series)
        assert isinstance(hist, pd.Series)
        # Histogram should be MACD - Signal
        assert np.allclose(hist[30:], macd[30:] - signal[30:], equal_nan=True)

    def test_bollinger_bands(self, sample_data):
        """Test Bollinger Bands calculation"""
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(sample_data)
        
        # Upper should be above middle, middle above lower
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] > middle[valid_idx]).all()
        assert (middle[valid_idx] > lower[valid_idx]).all()

    def test_atr_calculation(self, sample_data):
        """Test ATR calculation"""
        high = sample_data + np.random.uniform(0, 1, len(sample_data))
        low = sample_data - np.random.uniform(0, 1, len(sample_data))
        close = sample_data
        
        atr = TechnicalIndicators.calculate_atr(high, low, close)
        
        # ATR should be positive
        assert atr.dropna().min() >= 0
