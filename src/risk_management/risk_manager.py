"""Risk management and position sizing"""

from typing import Dict, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class PositionSize:
    """Position sizing information"""
    quantity: float
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float
    max_position_value: float


class RiskManager:
    """Manages trading risk and position sizing"""

    def __init__(self, config: Dict):
        """
        Initialize risk manager
        
        Args:
            config: Configuration dictionary with risk parameters
        """
        self.config = config
        self.account_balance = config.get('initial_capital', 10000)
        self.daily_pnl = 0
        self.open_positions = 0
        logger.info("Initialized risk manager")

    def calculate_position_size(self, entry_price: float, stop_loss: float,
                               account_balance: Optional[float] = None) -> PositionSize:
        """
        Calculate position size based on risk percentage
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            account_balance: Current account balance
            
        Returns:
            PositionSize object
        """
        if account_balance is None:
            account_balance = self.account_balance
        
        risk_per_trade = self.config.get('risk_per_trade', 0.02)
        risk_amount = account_balance * risk_per_trade
        
        # Calculate quantity based on risk
        price_difference = abs(entry_price - stop_loss)
        if price_difference == 0:
            quantity = 0
        else:
            quantity = risk_amount / price_difference
        
        # Apply max position size limit
        max_position_size = self.config.get('max_position_size', 0.1)
        max_quantity = account_balance * max_position_size / entry_price
        quantity = min(quantity, max_quantity)
        
        # Calculate potential reward
        take_profit_percent = self.config.get('take_profit_percent', 5)
        take_profit = entry_price * (1 + take_profit_percent / 100)
        reward_amount = (take_profit - entry_price) * quantity
        
        # Calculate risk/reward ratio
        if risk_amount > 0:
            risk_reward_ratio = reward_amount / risk_amount
        else:
            risk_reward_ratio = 0
        
        return PositionSize(
            quantity=quantity,
            risk_amount=risk_amount,
            reward_amount=reward_amount,
            risk_reward_ratio=risk_reward_ratio,
            max_position_value=quantity * entry_price
        )

    def can_open_position(self) -> bool:
        """
        Check if new position can be opened
        
        Returns:
            True if position can be opened
        """
        max_positions = self.config.get('max_open_positions', 3)
        return self.open_positions < max_positions

    def check_daily_loss_limit(self) -> bool:
        """
        Check if daily loss limit has been hit
        
        Returns:
            True if within loss limit
        """
        daily_limit = self.config.get('daily_loss_limit', 500)
        return self.daily_pnl > -daily_limit

    def update_daily_pnl(self, pnl: float):
        """
        Update daily P&L
        
        Args:
            pnl: Trade profit/loss
        """
        self.daily_pnl += pnl
        logger.info(f"Updated daily PnL: {self.daily_pnl:.2f}")

    def validate_trade(self, entry_price: float, stop_loss: float,
                      take_profit: float) -> bool:
        """
        Validate if trade meets risk management criteria
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            True if trade is valid
        """
        # Check if we can open new position
        if not self.can_open_position():
            logger.warning("Max open positions reached")
            return False
        
        # Check if within daily loss limit
        if not self.check_daily_loss_limit():
            logger.warning("Daily loss limit reached")
            return False
        
        # Check stop loss is below entry for long, above for short
        if stop_loss >= entry_price and take_profit > entry_price:
            logger.warning("Invalid stop loss or take profit")
            return False
        
        # Check minimum risk/reward ratio
        min_rr_ratio = 1.5
        if entry_price < take_profit:  # Long trade
            rr_ratio = (take_profit - entry_price) / (entry_price - stop_loss)
        else:  # Short trade
            rr_ratio = (entry_price - take_profit) / (stop_loss - entry_price)
        
        if rr_ratio < min_rr_ratio:
            logger.warning(f"Risk/reward ratio {rr_ratio:.2f} below minimum {min_rr_ratio}")
            return False
        
        return True
