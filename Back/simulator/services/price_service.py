# Back/simulator/services/price_service.py

import yfinance as yf

def fetch_current_price(stock_name):
    stock_mapping = {
        '삼성전자': '005930.KS',
        'SK하이닉스': '000660.KS',
        'LG에너지솔루션': '373220.KQ',
    }

    ticker = stock_mapping.get(stock_name)
    if not ticker:
        return 0  # 등록되지 않은 종목일 경우 0 반환

    stock = yf.Ticker(ticker)
    price = stock.info.get('currentPrice')  # 야후 API 기준 현재가

    if price is None:
        price = stock.history(period="1d")['Close'].iloc[-1]  # fallback

    return int(price)
