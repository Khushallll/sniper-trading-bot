"""
Live Market Data Fetcher - Real-time data from Binance
"""

import ccxt
import asyncio
from loguru import logger
from datetime import datetime
from typing import Dict, List, Optional


class LiveMarketDataFetcher:
    """Fetch real-time market data from Binance"""

    def __init__(self, exchange_name: str = "binance"):
        """Initialize with exchange"""
        self.exchange_name = exchange_name
        
        # Initialize Binance exchange (no API key needed for public data)
        if exchange_name == "binance":
            self.exchange = ccxt.binance()
        else:
            raise ValueError(f"Exchange {exchange_name} not supported yet")
        
        logger.info(f"✅ Initialized {exchange_name} market data fetcher")

    async def get_ohlcv_data(self, symbol: str, timeframe: str = "1m", limit: int = 100) -> List:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV data
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            logger.debug(f"✓ Fetched {len(ohlcv)} candles for {symbol} ({timeframe})")
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
            return []

    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Fetch current ticker data (price, volume, etc.)
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            
        Returns:
            Ticker data dictionary
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.debug(f"✓ Fetched ticker for {symbol}")
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    async def get_order_book(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """
        Fetch order book (bid/ask levels)
        
        Args:
            symbol: Trading pair
            limit: Depth of order book
            
        Returns:
            Order book data
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            logger.debug(f"✓ Fetched order book for {symbol}")
            return orderbook
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return None

    async def get_markets(self) -> List[str]:
        """
        Get list of available trading pairs
        
        Returns:
            List of trading pair symbols
        """
        try:
            symbols = self.exchange.symbols
            logger.debug(f"✓ Fetched {len(symbols)} available markets")
            return symbols
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def convert_ohlcv_to_dict(self, ohlcv: List) -> List[Dict]:
        """
        Convert OHLCV array format to dictionary format
        
        Args:
            ohlcv: Raw OHLCV data from exchange
            
        Returns:
            List of dictionaries with OHLCV data
        """
        result = []
        for candle in ohlcv:
            timestamp, open_price, high, low, close, volume = candle
            result.append({
                'timestamp': datetime.fromtimestamp(timestamp / 1000),
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        return result


async def demo_live_data():
    """Demo: Fetch real-time market data"""
    print("\n" + "="*80)
    print("DEMO 1: LIVE MARKET DATA FETCHER")
    print("="*80 + "\n")
    
    fetcher = LiveMarketDataFetcher("binance")
    
    # Fetch ticker data
    print("📊 Fetching current BTC/USDT price...")
    ticker = await fetcher.get_ticker("BTC/USDT")
    if ticker:
        print(f"✅ Current Price: ${ticker['last']:.2f}")
        print(f"   24h High: ${ticker['high']:.2f}")
        print(f"   24h Low: ${ticker['low']:.2f}")
        print(f"   24h Volume: {ticker['quoteVolume']:.2f} USDT\n")
    
    # Fetch OHLCV data
    print("📈 Fetching last 10 candles for BTC/USDT (1h timeframe)...")
    ohlcv = await fetcher.get_ohlcv_data("BTC/USDT", timeframe="1h", limit=10)
    if ohlcv:
        data = fetcher.convert_ohlcv_to_dict(ohlcv)
        print(f"✅ Fetched {len(data)} candles:")
        for i, candle in enumerate(data[-3:], 1):  # Show last 3
            print(f"   Candle {len(data)-3+i}: Open=${candle['open']:.2f}, "
                  f"Close=${candle['close']:.2f}, Volume={candle['volume']:,.0f}")
        print()
    
    # Fetch order book
    print("📊 Fetching order book for BTC/USDT...")
    orderbook = await fetcher.get_order_book("BTC/USDT", limit=5)
    if orderbook:
        print(f"✅ Order Book (Top 5 levels):")
        print(f"   Best Bid: ${orderbook['bids'][0][0]:.2f} ({orderbook['bids'][0][1]:.4f} BTC)")
        print(f"   Best Ask: ${orderbook['asks'][0][0]:.2f} ({orderbook['asks'][0][1]:.4f} BTC)\n")


if __name__ == "__main__":
    asyncio.run(demo_live_data())
