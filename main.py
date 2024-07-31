from auto_trader import AutoTrader


trader = AutoTrader()

price_threshold = 66200
amount_to_trade = 10
entry_price = 661178
profit_percentage = 10
loss_percentage = 97
# trader.trade(price_threshold, amount_to_trade)

# set amount to trade with
trader.set_amount(amount_to_trade)

trader.trade_config(entry_price, profit_percentage, loss_percentage, price_threshold)

trader.start_trade()