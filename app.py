import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def fetch_history(symbol):
    return yf.download(symbol, period="1y", interval="1d")


@st.cache_data(ttl=600)
def fetch_info(symbol):
    ticker = yf.Ticker(symbol)

    try:
        info = ticker.get_info()   # newer stable method
    except:
        info = ticker.info

    return info


@st.cache_data(ttl=600)
def fetch_financials(symbol):
    ticker = yf.Ticker(symbol)

    return {
        "income": ticker.financials,
        "balance": ticker.balance_sheet,
        "cashflow": ticker.cashflow
    }

def normalize_symbol(symbol):
    symbol = symbol.upper().strip()

    # NSE format fix
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = symbol + ".NS"

    return symbol

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from core_data_layer import fetch_history, fetch_info, fetch_financials
from symbol_cleaning import normalize_symbol

st.set_page_config(page_title="Pro Stock Dashboard", layout="wide")


st.title("📊 Pro Stock Intelligence Dashboard")


# -------------------------
# SEARCH
# -------------------------
symbol_input = st.text_input("Enter Stock (e.g. RELIANCE, TCS, INFY)")

go = st.button("GO 🚀")


if go and symbol_input:

    symbol = normalize_symbol(symbol_input)

    with st.spinner("Fetching market data..."):

        info = fetch_info(symbol)
        hist = fetch_history(symbol)
        fin = fetch_financials(symbol)

    # -------------------------
    # HEADER
    # -------------------------
    name = info.get("longName", symbol)

    st.header(name)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Current Price", info.get("currentPrice", "N/A"))
    col2.metric("Market Cap", info.get("marketCap", "N/A"))
    col3.metric("Volume", info.get("volume", "N/A"))
    col4.metric("P/E Ratio", info.get("trailingPE", "N/A"))


    # -------------------------
    # ABOUT
    # -------------------------
    st.subheader("📌 About")
    st.write(info.get("longBusinessSummary", "No data available"))


    # -------------------------
    # OVERVIEW TABLE
    # -------------------------
    st.subheader("📊 Overview")

    overview = {
        "Symbol": symbol,
        "52W High": info.get("fiftyTwoWeekHigh"),
        "52W Low": info.get("fiftyTwoWeekLow"),
        "Dividend Yield": info.get("dividendYield"),
        "Beta": info.get("beta")
    }

    st.dataframe([overview])


    # -------------------------
    # CHART (FIXED)
    # -------------------------
    st.subheader("📈 Price Chart")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        name="Close Price"
    ))

    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)


    # -------------------------
    # FINANCIALS
    # -------------------------
    st.subheader("📑 Financials")

    tab1, tab2, tab3 = st.tabs(["Income", "Balance Sheet", "Cash Flow"])

    with tab1:
        st.dataframe(fin["income"])

    with tab2:
        st.dataframe(fin["balance"])

    with tab3:
        st.dataframe(fin["cashflow"])


    # -------------------------
    # FOOTER
    # -------------------------
    st.caption(f"Last Updated: {datetime.now()}")
