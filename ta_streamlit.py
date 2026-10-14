from datetime import date

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Technical Analysis", layout="wide")

TICKERS = (
    "TCS.NS",
    "RELIANCE.NS",
    "HINDALCO.NS",
    "ADANIENT.NS",
    "HCLTECH.NS",
    "^NSEI",
    "INR=X",
)
OTHER = "Other..."


@st.cache_data(ttl=3600, show_spinner="Downloading prices...")
def load_prices(ticker: str, start: date, end: date) -> pd.DataFrame:
    return yf.Ticker(ticker).history(start=start, end=end).dropna()


def bollinger(df: pd.DataFrame, ticker: str):
    window = 20
    std_dev_factor = 2
    sma = df["Close"].rolling(window=window).mean()
    rf = df["Close"].rolling(window=window).std() * std_dev_factor

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df["Close"], label="Close Price", color="blue", linewidth=1)
    ax.plot(df.index, sma, label=f"{window}-Day SMA", color="orange", linewidth=1.5)
    ax.plot(df.index, sma + rf, label="Upper Bollinger Band", color="green", linestyle="--", linewidth=1)
    ax.plot(df.index, sma - rf, label="Lower Bollinger Band", color="red", linestyle="--", linewidth=1)
    ax.set_title(f"Bollinger Bands for {ticker} ({window}-day window)", fontsize=14)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.legend()
    ax.grid(alpha=0.3)
    return fig


def macd(df: pd.DataFrame, ticker: str):
    ema_short = df["Close"].ewm(span=12, adjust=False).mean()
    ema_long = df["Close"].ewm(span=26, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, macd_line, label="MACD", color="blue")
    ax.plot(df.index, signal_line, label="Signal Line", color="red")
    ax.bar(df.index, macd_line - signal_line, label="Histogram", color="gray", alpha=0.5)
    ax.set_title(f"MACD Indicator for {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("MACD Value")
    ax.legend(loc="best")
    ax.grid()
    return fig


def ma(df: pd.DataFrame, ticker: str):
    periods = [10, 20, 30, 40, 50, 60]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df["Close"], label="Price", color="black", linewidth=1.5)
    for period in periods:
        ax.plot(df.index, df["Close"].rolling(window=period).mean(), label=f"SMA {period}")
    ax.set_title(f"Moving Average Ribbon for {ticker}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid()
    return fig


def candle(df: pd.DataFrame, ticker: str):
    ohlcv = df[["Open", "High", "Low", "Close", "Volume"]]
    fig, _ = mpf.plot(
        ohlcv,
        type="candle",
        style="charles",
        volume=True,
        figsize=(12, 7),
        title=f"Candlestick Chart for {ticker}",
        warn_too_much_data=len(ohlcv) + 1,
        returnfig=True,
    )
    return fig


def cloud(df: pd.DataFrame, ticker: str):
    close = df["Close"]

    def mid(window: int) -> pd.Series:
        return (close.rolling(window=window).max() + close.rolling(window=window).min()) / 2

    tenkan = mid(9)
    kijun = mid(26)
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = mid(52).shift(26)
    chikou = close.shift(-26)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, close, label="Close Price", color="black")
    ax.plot(df.index, tenkan, label="Conversion Line", color="red")
    ax.plot(df.index, kijun, label="Base Line", color="blue")
    ax.fill_between(df.index, senkou_a, senkou_b, where=senkou_a >= senkou_b,
                    color="lightgreen", alpha=0.5, label="Cloud (Span A > Span B)")
    ax.fill_between(df.index, senkou_a, senkou_b, where=senkou_a < senkou_b,
                    color="lightcoral", alpha=0.5, label="Cloud (Span A < Span B)")
    ax.plot(df.index, chikou, label="Lagging Line", color="purple", linestyle="dotted")
    ax.set_title(f"Ichimoku Cloud for {ticker}")
    ax.legend()
    return fig


# label -> (header, plot function, minimum rows needed for the indicator to show)
PLOTS = {
    "MA": ("Moving Average Ribbons", ma, 60),
    "BOLL": ("Bollinger Bands", bollinger, 20),
    "MACD": ("MACD", macd, 35),
    "CANDLE": ("Candlestick", candle, 2),
    "CLOUD": ("Ichimoku Cloud", cloud, 78),
}


st.title("Technical Analysis")

choice = st.selectbox("Select Ticker", TICKERS + (OTHER,))
if choice == OTHER:
    ticker = st.text_input("Ticker symbol (any Yahoo Finance symbol)", "INFY.NS").strip().upper()
else:
    ticker = choice

plot = st.selectbox("Select Plot", ("NONE",) + tuple(PLOTS))

col_start, col_end = st.columns(2)
start = col_start.date_input("Start Date", date(2024, 1, 1))
end = col_end.date_input("End Date", date.today())

if plot != "NONE" and ticker:
    if start >= end:
        st.error("Start date must be before end date.")
    else:
        header, method, min_rows = PLOTS[plot]
        try:
            df = load_prices(ticker, start, end)
        except Exception as exc:
            st.error(f"Could not download data for {ticker}: {exc}")
            df = None

        if df is not None:
            if df.empty:
                st.warning(f"No price data found for {ticker} between {start} and {end}.")
            else:
                if len(df) < min_rows:
                    st.warning(
                        f"Only {len(df)} trading days available; {header} needs about "
                        f"{min_rows} to be fully drawn. Try an earlier start date."
                    )
                st.header(f"{header} - {ticker}")
                fig = method(df.copy(), ticker)
                st.pyplot(fig)
                plt.close(fig)
