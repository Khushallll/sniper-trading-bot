"""Fetch real-time market data from exchanges"""

import ccxt
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio
from loguru import logger


class MarketDataFetcher:
    """Fetches market data from cryptocurrency exchanges"""

    def __init__(self, exchange_name: str, api_key: str = None, api_secret: str = None):
        """
        Initialize market data fetcher
        
        Args:
            exchange_name: Name of exchange (e.g., 'binance')
            api_key: Exchange API key
            api_secret: Exchange API secret
        """
        self.exchange_name = exchange_name.lower()
        self.exchange_class = getattr(ccxt, self.exchange_name)
        
        params = {}
        if api_key and api_secret:
            params = {'apiKey': api_key, 'secret': api_secret}
        
        self.exchange = self.exchange_class(params)
        logger.info(f"Initialized {self.exchange_name} market data fetcher")

    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1m', 
                         limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV (candlestick) data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe (e.g., '1m', '5m', '1h')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv, symbol, timeframe, limit=limit
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            
            return df.set_index('timestamp')
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise

    async def fetch_ticker(self, symbol: str) -> Dict:
        """
        Fetch latest ticker information
        
        Args:
            symbol: Trading pair
            
        Returns:
            Ticker data dictionary
        """
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    async def fetch_order_book(self, symbol: str, limit: int = 20) -> Dict:
        """
        Fetch order book data
        
        Args:
            symbol: Trading pair
            limit: Number of orders to fetch
            
        Returns:
            Order book data
        """
        try:
            orderbook = await asyncio.to_thread(
                self.exchange.fetch_order_book, symbol, limit=limit
            )
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            raise

    async def fetch_trades(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch recent trades
        
        Args:
            symbol: Trading pair
            limit: Number of trades to fetch
            
        Returns:
            DataFrame with trade data
        """
        try:
            trades = await asyncio.to_thread(
                self.exchange.fetch_trades, symbol, limit=limit
            )
            
            df = pd.DataFrame(trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            raise
