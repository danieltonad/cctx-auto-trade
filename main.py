from auto_trader import AutoTrader


trader = AutoTrader()

price_threshold = 65000
amount_to_trade = 10

trader.trade(price_threshold, amount_to_trade)