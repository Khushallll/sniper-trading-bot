"""Tests for opportunity detection"""

import pytest
import pandas as pd
import numpy as np
from src.detection.opportunity_detector import OpportunityDetector


@pytest.fixture
def sample_ohlcv():
    """Create sample OHLCV data"""
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')
    data = {
        'open': np.random.uniform(100, 110, 100),
        'high': np.random.uniform(110, 120, 100),
        'low': np.random.uniform(90, 100, 100),
        'close': np.random.uniform(100, 110, 100),
        'volume': np.random.uniform(1000000, 2000000, 100)
    }
    df = pd.DataFrame(data, index=dates)
    return df


@pytest.fixture
def detector():
    """Create detector instance"""
    config = {
        'min_volume_threshold': 1000000,
        'price_change_threshold': 0.02,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'macd_signal_threshold': 0.0001
    }
    return OpportunityDetector(config)


class TestOpportunityDetector:
    """Test opportunity detection"""

    def test_detect_opportunities(self, sample_ohlcv, detector):
        """Test opportunity detection"""
        opportunities = detector.detect_opportunities(sample_ohlcv, 'BTC/USDT')
        
        # Should return a list
        assert isinstance(opportunities, list)
        # Each opportunity should have required attributes
        for opp in opportunities:
            assert hasattr(opp, 'symbol')
            assert hasattr(opp, 'confidence_score')
            assert hasattr(opp, 'entry_price')
            assert hasattr(opp, 'stop_loss')
            assert hasattr(opp, 'take_profit')

    def test_opportunity_confidence_range(self, sample_ohlcv, detector):
        """Test confidence score is valid"""
        opportunities = detector.detect_opportunities(sample_ohlcv, 'BTC/USDT')
        
        for opp in opportunities:
            # Confidence should be between 0 and 1
            assert 0 <= opp.confidence_score <= 1
