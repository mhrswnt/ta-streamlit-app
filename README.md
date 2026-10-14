# Technical Analysis Dashboard

A small Streamlit app that charts technical indicators for any Yahoo Finance ticker.
The indicator code comes from `charts_and_ta.ipynb`.

## Indicators

| Option | Chart |
|--------|-------|
| `MA` | Moving average ribbon (SMA 10/20/30/40/50/60) |
| `BOLL` | Bollinger bands (20-day SMA, 2 std dev) |
| `MACD` | MACD (12/26/9) with signal line and histogram |
| `CANDLE` | Candlestick chart with volume |
| `CLOUD` | Ichimoku cloud (9/26/52) |

## Run

```bash
pip install -r requirements.txt
streamlit run ta_streamlit.py
```

Pick a ticker (or choose "Other..." and type any Yahoo Finance symbol), choose a plot and a date range.
Price data is downloaded with `yfinance` and cached for an hour.
