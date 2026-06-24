import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Dashboard", layout="wide")

# ----------------------------
# 🔧 CACHE DATA
# ----------------------------
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    return stock


# ----------------------------
# 🔎 SEARCH HELPERS (AUTO-SUGGEST SIMPLIFIED)
# ----------------------------
COMMON_STOCKS = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Adani Enterprises": "ADANIENT.NS"
}

def autosuggest(query):
    return [name for name in COMMON_STOCKS.keys() if query.lower() in name.lower()]


# ----------------------------
# 📊 PRICE CHART
# ----------------------------
def plot_chart(data):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="Close Price"
    ))

    fig.update_layout(
        title="Stock Price Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    return fig


# ----------------------------
# 🧠 UI - SEARCH BAR
# ----------------------------
st.title("📊 Stock Market Dashboard")

query = st.text_input("Search Stock (Company Name or Symbol)")

suggestions = autosuggest(query) if query else []

if suggestions:
    st.write("Suggestions:")
    selected_name = st.selectbox("Select Stock", suggestions)
else:
    selected_name = None


col1, col2 = st.columns([3, 1])

with col1:
    stock_input = st.text_input("Or Enter Symbol (e.g. RELIANCE.NS)", "")

with col2:
    go = st.button("GO 🚀")


# ----------------------------
# 🚀 MAIN LOGIC
# ----------------------------
symbol = None

if go:
    if stock_input:
        symbol = stock_input.upper()
    elif selected_name:
        symbol = COMMON_STOCKS[selected_name]

    if symbol:
        stock = get_stock_data(symbol)

        info = stock.info
        hist = stock.history(period="1y")

        # ----------------------------
        # HEADER
        # ----------------------------
        st.header(f"{info.get('longName', 'N/A')}")

        price = info.get("currentPrice", info.get("regularMarketPrice"))

        col1, col2, col3 = st.columns(3)

        col1.metric("Current Price", price)
        col2.metric("Market Cap", info.get("marketCap"))
        col3.metric("Volume", info.get("volume"))

        # ----------------------------
        # ABOUT
        # ----------------------------
        st.subheader("📌 About Company")
        st.write(info.get("longBusinessSummary", "No description available"))

        # ----------------------------
        # OVERVIEW
        # ----------------------------
        st.subheader("📊 Overview")

        overview_data = {
            "NSE Symbol": symbol,
            "Market Cap": info.get("marketCap"),
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "P/E Ratio": info.get("trailingPE"),
            "Dividend Yield": info.get("dividendYield")
        }

        st.dataframe(pd.DataFrame([overview_data]))

        # ----------------------------
        # FINANCIALS
        # ----------------------------
        st.subheader("📑 Financials")

        tab1, tab2, tab3 = st.tabs(["Income", "Balance Sheet", "Cash Flow"])

        with tab1:
            st.dataframe(stock.financials)

        with tab2:
            st.dataframe(stock.balance_sheet)

        with tab3:
            st.dataframe(stock.cashflow)

        # ----------------------------
        # CHART
        # ----------------------------
        st.subheader("📈 Price Chart")
        st.plotly_chart(plot_chart(hist), use_container_width=True)

        st.caption(f"Last updated: {datetime.now()}")
    else:
        st.error("Please enter or select a valid stock")
