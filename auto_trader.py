from config import Config
import json
from ccxt import bybit
from pandas import DataFrame, read_json
from datetime import datetime
from time import sleep

class AutoTrader:
    symbol: str
    balance: dict
    exchange: bybit
    ticker: dict
    entry_price: float
    take_profit_price: float
    stop_loss_price: float
    buy_price_threshold: int
    min_btc: float = 0.0001
    amount: int
    proceed_trading: bool
    initial_order_id: str
    exit_order_id: str
    
    def __init__(self) -> None:
        config = Config()
        self.exchange = bybit({
            'apiKey': config.API_KEY,
            'secret': config.API_SECERET,
        })
        
        self.symbol = config.TICKER_SYMBOL
        self.exchange.set_sandbox_mode(True)
        self.exchange.options["defaultType"] = "future"
        self.balance = self.exchange.fetch_balance()
        self.ticker = self.exchange.fetch_ticker(self.symbol)
        
    def set_amount(self, amount: int):
        last = float(self.ticker['last'])
        btc_amount = amount / last
        
        if btc_amount < self.min_btc:
            min_usd = int(self.min_btc * last)
            raise ValueError(f"Amount less than minimum \nMinimum Amount: {min_usd:,.2f} USDT")
        # proceed to set amount
        self.amount = amount
        
    def trade_config(self, entry_price: float, profit_percentage: float, loss_percentage, buy_price_threshold: float):
        if not self.amount:
            raise ValueError("Setup amount before trade configuration ")
            
        self.entry_price = entry_price
        self.buy_price_threshold = buy_price_threshold
        self.stop_loss_price = self.entry_price * (1 - (loss_percentage / 100))
        self.take_profit_price = self.entry_price * (1 + (profit_percentage / 100))
        
        
    def set_amount(self, amount: int):
        last = float(self.ticker['last'])
        btc_amount = amount / last
        # validate min amount
        if btc_amount < self.min_btc:
            min_usd = int(self.min_btc * last)
            raise ValueError(f"Amount less than minimum \nMinimum Amount: {min_usd:,.2f} USDT")
        
        self.amount = amount
        
    def __get_current_price(self) -> float:
        ticker = self.exchange.fetch_ticker(self.symbol)
        return float(ticker['last'])

    # Function to place an initial order
    def __place_initial_order(self, trade_amount) -> dict:
        return self.exchange.create_order(symbol=self.symbol, type='market', side='buy', amount=trade_amount)

    # Function to calculate profit/loss
    def __calculate_profit_loss(self, current_price, trade_amount):
        profit_loss = (current_price - self.entry_price) * trade_amount
        percentage = ((current_price - self.entry_price) / self.entry_price) * 100
        return profit_loss, percentage

    # Function to save trading history
    def __save_trading_history(self, trade_data):
        prev_data = []
        with open(Config.REPORT_FILE, "r") as file:
            prev_data =  json.load(file)
            prev_data.append(trade_data)
        with open(Config.REPORT_FILE, "w") as file:
            json.dump(prev_data, file)

    # Monitor and execute based on profit/loss conditions
    def __auto_execute_trade(self, trade_amount):
        try:
            while True:
                current_price = self.__get_current_price()
                profit_loss, percentage = self.__calculate_profit_loss(current_price, trade_amount)
                print(f"Current Price: {current_price} USDT | Profit/Loss: {profit_loss:,.2f} USDT ({percentage:,.2f}%) \n")

                if current_price >= self.take_profit_price:
                    # Place a take-profit sell order
                    take_profit_order = self.exchange.create_order(symbol=self.symbol, type='market', side='sell', amount=trade_amount)
                    self.exit_order_id = take_profit_order.get("info").get("orderId")
                    print(f"Take-profit order executed at {current_price} USDT")
                    self.__save_trading_history({
                        'time': datetime.now().isoformat(),
                        'symbol': self.symbol,
                        'initial_order_id': self.initial_order_id,
                        'exit_order_id': self.exit_order_id,
                        'exit_type': 'take-profit',
                        'price': current_price,
                        'amount': self.amount,
                        'profit_loss': profit_loss,
                        'percentage': percentage,
                    })
                    break

                if current_price <= self.stop_loss_price:
                    # Place a stop-loss sell order
                    stop_loss_order = self.exchange.create_order(symbol=self.symbol, type='market', side='sell', amount=trade_amount)
                    self.exit_order_id = stop_loss_order.get("info").get("orderId")
                    print(f"Stop-loss order executed at {current_price} USDT")
                    self.__save_trading_history({
                        'time': datetime.now().isoformat(),
                        'symbol': self.symbol,
                        'initial_order_id': self.initial_order_id,
                        'exit_order_id': self.exit_order_id,
                        'exit_type': 'stop-loss',
                        'price': current_price,
                        'amount': self.amount,
                        'profit_loss': profit_loss,
                        'percentage': percentage,
                    })
                    break

                sleep(5)  # monitor every 5 seconds
                
        except KeyboardInterrupt:
            print("Stopped monitoring...")
 

    def start_trade(self):
        last = float(self.ticker['last'])
        trade_amount = self.amount / last
        
        balance = self.balance[self.symbol.split('/')[-1]]['free']
        if balance < self.amount:
            raise ValueError(f"Insufficient Balance to trade \nCurrent Balance: {balance:,.2f}")
            
        print("Staring trade ...")
            
        if self.should_enter_trade(self.buy_price_threshold, self.amount):
            try:
                order = self.__place_initial_order(trade_amount)
                order_id = order.get("info").get("orderId")
                # order_details = self.exchange.fetch_open_order(order_id, symbol=self.symbol)
                print(f"[Initial Order Placed] id => {order_id}")
                self.initial_order_id = order_id
                
                # monitor trading
                self.__auto_execute_trade(trade_amount)
                
            except Exception as e:
                raise NotImplementedError(f"An error occurred: {e}")
                
        else:
            print("Trading Conditions not met!, Retrying after 5 seconds.")
            sleep(5)
            self.start_trade(self)

    
    # Trading decision based on strategy
    def should_enter_trade(self, buy_price_threshold: float, trade_amount: float):
        if float(self.ticker['last']) < buy_price_threshold and self.balance[self.symbol.split('/')[-1]]['free'] >= trade_amount:
            return True
        return False
    
    def get_order_details(self, order_id: str):
        self.exchange.fetch_open_order(id=order_id, symbol=self.symbol)
        
        


    # Generate profit/loss report
    def generate_report(self):
        df = DataFrame(read_json(Config.REPORT_FILE))
        df['profit_loss'] = df['price'] * df['amount']
        df.to_csv('crypto_trading_report.csv')
        print(df)