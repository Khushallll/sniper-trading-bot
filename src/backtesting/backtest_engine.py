"""Backtesting engine for strategy validation"""

import pandas as pd
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


@dataclass
class BacktestResult:
    """Backtesting results"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    profit_factor: float
    sharpe_ratio: float
    avg_trade_duration: float


class BacktestEngine:
    """Backtests trading strategies"""

    def __init__(self, config: Dict):
        """
        Initialize backtesting engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.trades: List[Dict] = []
        logger.info("Initialized backtesting engine")

    def backtest(self, ohlcv_data: pd.DataFrame, 
                 signals: pd.Series) -> BacktestResult:
        """
        Run backtest on strategy signals
        
        Args:
            ohlcv_data: Historical OHLCV data
            signals: Trading signals (1 for buy, -1 for sell, 0 for hold)
            
        Returns:
            BacktestResult object
        """
        trades = []
        position = None
        entry_price = 0
        entry_time = None
        
        # Iterate through signals
        for i in range(len(signals)):
            if signals.iloc[i] == 1 and position is None:  # Buy signal
                position = 'long'
                entry_price = ohlcv_data['close'].iloc[i]
                entry_time = ohlcv_data.index[i]
            
            elif signals.iloc[i] == -1 and position == 'long':  # Sell signal
                exit_price = ohlcv_data['close'].iloc[i]
                exit_time = ohlcv_data.index[i]
                pnl = (exit_price - entry_price) * 100  # Assuming 100 units
                
                trade = {
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'entry_time': entry_time,
                    'exit_time': exit_time,
                    'duration': (exit_time - entry_time).total_seconds() / 3600  # Hours
                }
                trades.append(trade)
                position = None
        
        self.trades = trades
        return self._calculate_metrics(trades)

    def _calculate_metrics(self, trades: List[Dict]) -> BacktestResult:
        """
        Calculate backtest metrics
        
        Args:
            trades: List of completed trades
            
        Returns:
            BacktestResult object
        """
        if not trades:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                total_pnl=0,
                max_drawdown=0,
                profit_factor=0,
                sharpe_ratio=0,
                avg_trade_duration=0
            )
        
        pnls = [t['pnl'] for t in trades]
        total_pnl = sum(pnls)
        winning_trades = sum(1 for p in pnls if p > 0)
        losing_trades = len(pnls) - winning_trades
        
        win_rate = winning_trades / len(pnls) if pnls else 0
        
        # Calculate profit factor
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Calculate max drawdown
        cumulative_pnl = pd.Series(pnls).cumsum()
        running_max = cumulative_pnl.expanding().max()
        drawdowns = (cumulative_pnl - running_max) / running_max
        max_drawdown = abs(drawdowns.min())
        
        # Calculate Sharpe ratio (simplified)
        returns = pd.Series(pnls).pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() if len(returns) > 0 else 0
        
        # Average trade duration
        durations = [t['duration'] for t in trades]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return BacktestResult(
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            avg_trade_duration=avg_duration
        )
