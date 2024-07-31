from auto_trader import AutoTrader


trader = AutoTrader()

price_threshold = 66600
amount_to_trade = 10
entry_price = 66678
profit_percentage = 2
loss_percentage = 5.1

# set amount to trade with
trader.set_amount(amount_to_trade)

# configure trading creteria
trader.trade_config(entry_price, profit_percentage, loss_percentage, price_threshold)

# start auto trading
trader.start_trade()

# generate all reports
trader.generate_report()