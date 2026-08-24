"""Execute trades on exchange"""

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


@dataclass
class ExecutedTrade:
    """Represents an executed trade"""
    symbol: str
    order_id: str
    timestamp: datetime
    side: str  # 'buy' or 'sell'
    entry_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    status: str  # 'open', 'closed', 'cancelled'
    pnl: Optional[float] = None


class TradeExecutor:
    """Executes trades on exchange"""

    def __init__(self, exchange, config: Dict):
        """
        Initialize trade executor
        
        Args:
            exchange: CCXT exchange instance
            config: Configuration dictionary
        """
        self.exchange = exchange
        self.config = config
        self.open_trades: Dict[str, ExecutedTrade] = {}
        logger.info("Initialized trade executor")

    async def execute_market_order(self, symbol: str, side: str, quantity: float,
                                  stop_loss: float, take_profit: float) -> Optional[ExecutedTrade]:
        """
        Execute a market order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Order quantity
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            ExecutedTrade object or None if execution failed
        """
        try:
            # Execute market order
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol, side, quantity
            )
            
            trade = ExecutedTrade(
                symbol=symbol,
                order_id=order['id'],
                timestamp=datetime.now(),
                side=side,
                entry_price=order.get('average', 0),
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                status='open'
            )
            
            self.open_trades[order['id']] = trade
            logger.info(f"Executed {side} order: {symbol} {quantity} @ {trade.entry_price}")
            
            return trade
        except Exception as e:
            logger.error(f"Error executing market order: {e}")
            return None

    async def execute_limit_order(self, symbol: str, side: str, quantity: float,
                                 price: float, stop_loss: float, 
                                 take_profit: float) -> Optional[ExecutedTrade]:
        """
        Execute a limit order
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Order quantity
            price: Limit price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            ExecutedTrade object or None if execution failed
        """
        try:
            order = await asyncio.to_thread(
                self.exchange.create_limit_order,
                symbol, side, quantity, price
            )
            
            trade = ExecutedTrade(
                symbol=symbol,
                order_id=order['id'],
                timestamp=datetime.now(),
                side=side,
                entry_price=price,
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                status='open'
            )
            
            self.open_trades[order['id']] = trade
            logger.info(f"Placed limit {side} order: {symbol} {quantity} @ {price}")
            
            return trade
        except Exception as e:
            logger.error(f"Error executing limit order: {e}")
            return None

    async def close_trade(self, order_id: str, exit_price: float) -> Optional[ExecutedTrade]:
        """
        Close an open trade
        
        Args:
            order_id: Order ID to close
            exit_price: Exit price
            
        Returns:
            Updated ExecutedTrade object
        """
        if order_id not in self.open_trades:
            logger.warning(f"Order {order_id} not found")
            return None
        
        trade = self.open_trades[order_id]
        
        # Calculate PnL
        if trade.side == 'buy':
            pnl = (exit_price - trade.entry_price) * trade.quantity
        else:
            pnl = (trade.entry_price - exit_price) * trade.quantity
        
        trade.pnl = pnl
        trade.status = 'closed'
        
        logger.info(f"Closed trade {order_id}: PnL = {pnl:.2f}")
        
        return trade

    async def set_stop_loss(self, order_id: str, stop_price: float):
        """
        Set stop loss for a trade
        
        Args:
            order_id: Order ID
            stop_price: Stop loss price
        """
        try:
            if order_id in self.open_trades:
                self.open_trades[order_id].stop_loss = stop_price
                logger.info(f"Set stop loss for {order_id}: {stop_price}")
        except Exception as e:
            logger.error(f"Error setting stop loss: {e}")

    async def set_take_profit(self, order_id: str, profit_price: float):
        """
        Set take profit for a trade
        
        Args:
            order_id: Order ID
            profit_price: Take profit price
        """
        try:
            if order_id in self.open_trades:
                self.open_trades[order_id].take_profit = profit_price
                logger.info(f"Set take profit for {order_id}: {profit_price}")
        except Exception as e:
            logger.error(f"Error setting take profit: {e}")
