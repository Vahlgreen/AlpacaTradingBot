import json
import datetime as dt
import pandas as pd
import os

from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient, StockBarsRequest, StockLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, TimeInForce

from parameters import live_parameters
from functions import *
from indicators import *

# Read api keys
path = "Resources/APIKEYS/alpaca.json"
with open(path, "r") as file:
    api_keys = json.load(file)

# Get current s&p 500 tickers
try:
    tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Symbol"].to_list()
except Exception as e:
    raise ValueError(f"Unable to load tickers. Failed with exception {e}")





# Establish portfolio parameters

trading_client = TradingClient(api_keys["api_key"], api_keys["api_key_secret"], paper=True)
stock_client = StockHistoricalDataClient(api_keys["api_key"], api_keys["api_key_secret"])
account = trading_client.get_account()


# Create portfolio
start_date = str(dt.datetime.today().strftime('%Y-%m-%d'))
end_date = str(dt.datetime.today() + dt.timedelta(days=1000))
# if os.path.isfile(f"Resources/Portfolios/portfolio{start_date-dt.timedelta(days=1)}.pkl"):
#     portfolio

# portfolio = Portfolio(start_date, end_date, strategies=live_parameters["strategies"], funds=account.cash, transaction_fee=live_parameters["transaction_fee"])



# Get historical data
request_params = StockBarsRequest(
    symbol_or_symbols=tickers,
    timeframe=TimeFrame.Day,
    start=dt.date.today() - dt.timedelta(days=300)
)
bars = stock_client.get_stock_bars(request_params)
bars_df = bars.df
bars_df.columns = ["Open","High","Low","Close","Volume","Trade_count","Vwap"]

quote_request_params = StockLatestQuoteRequest(symbol_or_symbols=tickers)
quotes = stock_client.get_stock_latest_quote(quote_request_params)

strat_tickers = ["AAPL", "TSLA"]


def get_buy_signal(stock_data: pd.DataFrame,current_date: str) -> bool:
    signal = False
    if moving_average(stock_data, current_date):
        if rsi(stock_data, current_date):
            signal = True
    return signal

def get_sell_signal(stock_data: pd.DataFrame, current_date: str) -> bool:
    signal = False

    if not moving_average(stock_data,current_date):
        if not rsi(stock_data, current_date):
            signal = True
    return signal
#"429- Too Many Requests"



positions = trading_client.get_all_positions()
tickers_in_holdings = {position.symbol: position for position in positions}

# Cancel all unfilled orders from yesterday
request_params = GetOrdersRequest(
                    status='all',
                    side=OrderSide.BUY
                 )# orders that satisfy params
orders = trading_client.get_orders(filter=request_params)

for order in orders:
    if order.status != "filled":
        trading_client.cancel_order_by_id(order.id)


# Main loop
for i, ticker in enumerate(tickers, start=1):

    if ticker in tickers_in_holdings.keys():
        data = bars_df.loc[ticker]
        data["Date"] = data.index
        data["Date"] = data["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))

        if get_sell_signal(data, start_date):
            trading_client.close_position(ticker)

    elif ticker in strat_tickers:
        data = bars_df.loc[ticker]
        data["Date"] = data.index
        data["Date"] = data["Date"].apply(lambda x: x.strftime('%Y-%m-%d'))


        if get_buy_signal(data,start_date):

            market_order_data = MarketOrderRequest(
                               symbol=ticker,
                               qty=1,
                               side=OrderSide.BUY,
                               time_in_force=TimeInForce.DAY
                               )

            market_order = trading_client.submit_order(
                           order_data=market_order_data
                          )

print("")



############################# News #############################
#
# symbols = 'TSLA'
# start_date = "2021-09-01T00:00:00Z"
# end_date = "2021-09-30T11:59:59Z"
# url = f'https://data.alpaca.markets/v1beta1/news?start={start_date}&end={end_date}&symbols={symbols}'
# headers = {'content-type': 'application/json', 'Apca-Api-Key-Id': api_key, 'Apca-Api-Secret-Key': api_secret}
# response = requests.get(url, headers=headers)
# response_dict = json.loads(response.text)
# for i in response_dict:
#     print("key: ", i, "val: ", response_dict[i])



############################# Cancel orders #############################
# cancel_status = trading_client.cancel_order_by_id(market_order.id)
# print(cancel_status)

############################ Get orders ################################
# request_params = GetOrdersRequest(
#                     status='open',
#                     side=OrderSide.BUY
#                  )# orders that satisfy params
# orders = trading_client.get_orders(filter=request_params)

#'status': <OrderStatus.FILLED: 'filled'>,