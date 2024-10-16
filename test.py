import json
import datetime as dt
import pandas as pd
import os

from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient, StockBarsRequest, StockLatestQuoteRequest
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest, LimitOrderRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.enums import OrderSide, TimeInForce
from portfolio import Portfolio
from parameters import live_parameters


# Read api keys
path = "Resources/APIKEYS/alpaca.json"
with open(path, "r") as file:
    api_keys = json.load(file)

# Get current s&p 500 tickers
try:
    tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]["Symbol"].to_list()
except Exception as e:
    raise ValueError(f"Unable to load tickers. Failed with exception {e}")


trading_client = TradingClient(api_keys["api_key"], api_keys["api_key_secret"], paper=True)
stock_client = StockHistoricalDataClient(api_keys["api_key"], api_keys["api_key_secret"])
account = trading_client.get_account()

ticker = "TSLA"
quote_request_params = StockLatestQuoteRequest(symbol_or_symbols=ticker)
quote = stock_client.get_stock_latest_quote(quote_request_params)
current_price = quote[ticker].ask_price
if quote[ticker].ask_size > 1:
    current_price = current_price / quote[ticker].ask_size

# loss, type of order
limit_Order = LimitOrderRequest(
                    limit_price = current_price,
                    symbol=ticker,
                    qty=1,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    )

market_order = trading_client.submit_order(
               order_data=limit_Order
              )

############################# Print all orders ################################

request_params = GetOrdersRequest(
                    status='all',
                    side=OrderSide.BUY
                 )# orders that satisfy params
orders = trading_client.get_orders(filter=request_params)
for order in orders:
    print(order)