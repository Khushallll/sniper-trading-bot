"""Main entry point for Sniper Trading Bot"""

import asyncio
import json
from pathlib import Path
from loguru import logger
from src.market_data.data_fetcher import MarketDataFetcher
from src.detection.opportunity_detector import OpportunityDetector
from src.execution.executor import TradeExecutor
from src.risk_management.risk_manager import RiskManager


class SniperTradingBot:
    """Main trading bot class"""

    def __init__(self, config_path: str = 'config/settings.json'):
        """
        Initialize the trading bot
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize modules
        exchange_config = self.config['exchange']
        self.data_fetcher = MarketDataFetcher(
            exchange_config['name'],
            exchange_config.get('api_key'),
            exchange_config.get('api_secret')
        )
        
        self.opportunity_detector = OpportunityDetector(self.config['detection'])
        self.risk_manager = RiskManager(self.config['trading'])
        self.trade_executor = TradeExecutor(
            self.data_fetcher.exchange,
            self.config['trading']
        )
        
        logger.add(
            self.config['logging']['file'],
            level=self.config['logging']['level']
        )
        logger.info("Sniper Trading Bot initialized")

    def _load_config(self, config_path: str) -> dict:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            return json.load(f)

    async def run(self):
        """
        Main bot loop
        """
        logger.info("Starting bot main loop")
        
        trading_pairs = self.config['trading']['trading_pairs']
        timeframe = self.config['trading']['timeframe']
        
        try:
            while True:
                for pair in trading_pairs:
                    try:
                        # Fetch market data
                        ohlcv = await self.data_fetcher.fetch_ohlcv(
                            pair, timeframe, limit=100
                        )
                        
                        # Detect opportunities
                        opportunities = self.opportunity_detector.detect_opportunities(
                            ohlcv, pair
                        )
                        
                        # Process opportunities
                        for opp in opportunities:
                            logger.info(
                                f"Opportunity detected: {opp.symbol} "
                                f"({opp.signal_type}) @ {opp.entry_price} "
                                f"(Confidence: {opp.confidence_score:.2%})"
                            )
                            
                            # Validate with risk manager
                            if self.risk_manager.validate_trade(
                                opp.entry_price, opp.stop_loss, opp.take_profit
                            ):
                                # Calculate position size
                                pos_size = self.risk_manager.calculate_position_size(
                                    opp.entry_price, opp.stop_loss
                                )
                                
                                logger.info(
                                    f"Position size calculated: "
                                    f"{pos_size.quantity:.4f} {pair} "
                                    f"(Risk: {pos_size.risk_amount:.2f}, "
                                    f"RR Ratio: {pos_size.risk_reward_ratio:.2f})"
                                )
                                
                                # Execute trade (in sandbox mode by default)
                                if not self.config['exchange'].get('sandbox_mode', True):
                                    await self.trade_executor.execute_market_order(
                                        pair,
                                        'buy' if opp.signal_type == 'bullish' else 'sell',
                                        pos_size.quantity,
                                        opp.stop_loss,
                                        opp.take_profit
                                    )
                            else:
                                logger.warning(
                                    f"Trade validation failed for {opp.symbol}"
                                )
                    
                    except Exception as e:
                        logger.error(f"Error processing {pair}: {e}")
                        continue
                
                # Wait before next iteration
                await asyncio.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in bot loop: {e}")
            raise


async def main():
    """
    Application entry point
    """
    bot = SniperTradingBot()
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
