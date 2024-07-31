from config import Config
import ccxt
from ccxt import bybit
import pandas as pd


class AutoTrader:
    symbol: str = None
    balance: dict = None
    exchange: bybit = None
    
    def __init__(self) -> None:
        config = Config()
        self.exchange = bybit({
            'apiKey': config.API_KEY,
            'secret': config.API_SECERET,
        })
        self.exchange.set_sandbox_mode(True)
        self.exchange.options["defaultType"] = "future"
        self.balance = self.exchange.fetch_balance()
        self.symbol = config.TICKER_SYMBOL
 

    # Trading strategy example (simplified)
    def trade(self):
        ticker = self.exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        
        # Example strategy: Buy if balance allows, sell if we have BTC
        if self.balance['USDT']['free'] > price:
            order = self.exchange.create_market_buy_order('BTC/USDT', 1)
        elif self.balance['BTC']['free'] > 0:
            order = self.exchange.create_market_sell_order('BTC/USDT', 1)
        return order
    
    # Generate profit/loss report
    def generate_report(self):
        trades = self.exchange.fetch_my_trades('BTC/USDT')
        df = pd.DataFrame(trades)
        df['profit_loss'] = df['price'] * df['amount']
        # df.to_csv('crypto_trading_report.csv')
        print(df)
        
        
    def test(self):
        order = self.exchange.create_order(symbol=self.symbol, type='Market', side='Buy', amount=0.03)
        print(self.exchange.symbols)
        
        orders = self.exchange.fetch_open_orders(symbol=self.symbol)
        print("\n\n", orders)

