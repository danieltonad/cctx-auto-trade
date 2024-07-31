from config import Config
import ccxt
from ccxt import bybit
import pandas as pd


class AutoTrader:
    symbol: str = None
    balance: dict = None
    exchange: bybit = None
    ticker: bybit.tickers = None
    min_btc: float = 0.0001
    
    def __init__(self) -> None:
        config = Config()
        self.exchange = bybit({
            'apiKey': config.API_KEY,
            'secret': config.API_SECERET,
        })
        # self.exchange.verbose = True
        self.exchange.set_sandbox_mode(True)
        self.exchange.options["defaultType"] = "future"
        self.balance = self.exchange.fetch_balance()
        self.symbol = config.TICKER_SYMBOL
        self.ticker = self.exchange.fetch_ticker(self.symbol)
 

    def trade(self, buy_price_threshold: float, amount_to_invest: float):
        last = float(self.ticker['last'])
        btc_amount = amount_to_invest / last
        
        if btc_amount < self.min_btc:
            min_usd = int(self.min_btc * last)
            print(f"Minimum USDT: {min_usd:,.2f}")
            return
        
        balance = self.balance[self.symbol.split('/')[-1]]['free']
        if balance < amount_to_invest:
            print(f"Insufficient Balance to trade \nCurrent Balance: {balance:,.2f}")
            return
            
            
        if self.should_enter_trade(buy_price_threshold, amount_to_invest):
            try:
                order = self.exchange.create_order(symbol=self.symbol, type='market', side='buy', amount=btc_amount)
                order_id = order.get("info").get("orderId")
                order_details = self.exchange.fetch_open_order(order_id, symbol=self.symbol)
                
                print(f"Order placed: {order_details}")
            except Exception as e:
                print(f"An error occurred: {e}")
                
        else:
            print("Trading Conditions not met! ")
        
    
    
    def create_take_profit_order(self, amount, entry_price, take_profit_price):
        # Place the initial buy order
        buy_order = self.exchange.create_order(symbol=self.symbol, type='market', side='buy', amount=amount)
        print(f"Buy order placed: {buy_order}")
        
        # Calculate take profit order price
        if take_profit_price <= entry_price:
            print("Take profit price must be higher than the entry price for a long position.")
            return

        # Place the take profit sell order
        take_profit_order = self.exchange.create_order(
            symbol=self.symbol,
            type='limit',
            side='sell',
            amount=amount,
            price=take_profit_price,
            params={'reduce_only': True}  # Ensure this order only reduces the position
        )
        print(f"Take profit order placed: {take_profit_order}")
    
    
    
    # Trading decision based on strategy
    def should_enter_trade(self, buy_price_threshold: float, amount_to_invest: float):
        if float(self.ticker['last']) < buy_price_threshold and self.balance[self.symbol.split('/')[-1]]['free'] >= amount_to_invest:
            return True
        return False
    
    def get_order_details(self, order_id: str):
        self.exchange.fetch_open_order(id=order_id, symbol=self.symbol)
        
        
        
    def test(self):
        self.exchange.create_market_buy_order()
        order = self.exchange.create_order(symbol=self.symbol, type='market', side='buy', amount=0.0001)
        order_id = order.get("info").get("orderId")
        # print(self.balance, "\n\n")
        
        # orders = self.exchange.fetch_open_orders(symbol=self.symbol)
        # print("\n\n", orders)
        
        
        # order_details = self.exchange.fetch_open_order(id=order_id, symbol="BTC/USDT")
        # print(order_details)


    # Generate profit/loss report
    def generate_report(self):
        trades = self.exchange.fetch_my_trades('BTC/USDT')
        df = pd.DataFrame(trades)
        df['profit_loss'] = df['price'] * df['amount']
        # df.to_csv('crypto_trading_report.csv')
        print(df)