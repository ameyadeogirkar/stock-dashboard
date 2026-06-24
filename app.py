from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots


st.set_page_config(
    page_title="Stock Research Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)


INDIAN_STOCKS = [
    {"name": "Reliance Industries", "nse": "RELIANCE", "bse": "500325", "sector": "Energy"},
    {"name": "Tata Consultancy Services", "nse": "TCS", "bse": "532540", "sector": "Technology"},
    {"name": "HDFC Bank", "nse": "HDFCBANK", "bse": "500180", "sector": "Financial Services"},
    {"name": "ICICI Bank", "nse": "ICICIBANK", "bse": "532174", "sector": "Financial Services"},
    {"name": "Infosys", "nse": "INFY", "bse": "500209", "sector": "Technology"},
    {"name": "Hindustan Unilever", "nse": "HINDUNILVR", "bse": "500696", "sector": "Consumer Defensive"},
    {"name": "ITC", "nse": "ITC", "bse": "500875", "sector": "Consumer Defensive"},
    {"name": "State Bank of India", "nse": "SBIN", "bse": "500112", "sector": "Financial Services"},
    {"name": "Bharti Airtel", "nse": "BHARTIARTL", "bse": "532454", "sector": "Communication Services"},
    {"name": "Larsen & Toubro", "nse": "LT", "bse": "500510", "sector": "Industrials"},
    {"name": "Axis Bank", "nse": "AXISBANK", "bse": "532215", "sector": "Financial Services"},
    {"name": "Kotak Mahindra Bank", "nse": "KOTAKBANK", "bse": "500247", "sector": "Financial Services"},
    {"name": "Asian Paints", "nse": "ASIANPAINT", "bse": "500820", "sector": "Basic Materials"},
    {"name": "Maruti Suzuki India", "nse": "MARUTI", "bse": "532500", "sector": "Consumer Cyclical"},
    {"name": "Mahindra & Mahindra", "nse": "M&M", "bse": "500520", "sector": "Consumer Cyclical"},
    {"name": "Titan Company", "nse": "TITAN", "bse": "500114", "sector": "Consumer Cyclical"},
    {"name": "Sun Pharmaceutical", "nse": "SUNPHARMA", "bse": "524715", "sector": "Healthcare"},
    {"name": "Dr. Reddy's Laboratories", "nse": "DRREDDY", "bse": "500124", "sector": "Healthcare"},
    {"name": "Tata Motors", "nse": "TATAMOTORS", "bse": "500570", "sector": "Consumer Cyclical"},
    {"name": "Tata Steel", "nse": "TATASTEEL", "bse": "500470", "sector": "Basic Materials"},
    {"name": "Adani Enterprises", "nse": "ADANIENT", "bse": "512599", "sector": "Industrials"},
    {"name": "Adani Ports", "nse": "ADANIPORTS", "bse": "532921", "sector": "Industrials"},
    {"name": "Wipro", "nse": "WIPRO", "bse": "507685", "sector": "Technology"},
    {"name": "Nestle India", "nse": "NESTLEIND", "bse": "500790", "sector": "Consumer Defensive"},
    {"name": "UltraTech Cement", "nse": "ULTRACEMCO", "bse": "532538", "sector": "Basic Materials"},
    {"name": "Power Grid Corporation", "nse": "POWERGRID", "bse": "532898", "sector": "Utilities"},
    {"name": "NTPC", "nse": "NTPC", "bse": "532555", "sector": "Utilities"},
    {"name": "Oil and Natural Gas Corporation", "nse": "ONGC", "bse": "500312", "sector": "Energy"},
    {"name": "Bajaj Finance", "nse": "BAJFINANCE", "bse": "500034", "sector": "Financial Services"},
    {"name": "Bajaj Finserv", "nse": "BAJAJFINSV", "bse": "532978", "sector": "Financial Services"},
    {"name": "HCL Technologies", "nse": "HCLTECH", "bse": "532281", "sector": "Technology"},
    {"name": "Tech Mahindra", "nse": "TECHM", "bse": "532755", "sector": "Technology"},
]


PERIOD_CONFIG = {
    "1D": {"period": "1d", "interval": "5m"},
    "5D": {"period": "5d", "interval": "15m"},
    "1M": {"period": "1mo", "interval": "1d"},
    "6M": {"period": "6mo", "interval": "1d"},
    "1Y": {"period": "1y", "interval": "1d"},
    "5Y": {"period": "5y", "interval": "1wk"},
    "Max": {"period": "max", "interval": "1mo"},
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --card-bg: rgba(255, 255, 255, 0.82);
                --border: rgba(127, 127, 127, 0.18);
                --muted: #6b7280;
                --gain: #16803c;
                --loss: #c43333;
                --surface: rgba(245, 247, 250, 0.82);
            }
            [data-theme="dark"] {
                --card-bg: rgba(22, 27, 34, 0.84);
                --border: rgba(240, 246, 252, 0.16);
                --muted: #a8b3c2;
                --surface: rgba(13, 17, 23, 0.72);
            }
            .block-container {
                padding-top: 1.35rem;
                padding-bottom: 3rem;
                max-width: 1420px;
            }
            div[data-testid="stMetric"] {
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 16px 16px 14px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            }
            div[data-testid="stMetricLabel"] p {
                color: var(--muted);
                font-size: 0.82rem;
            }
            div[data-testid="stMetricValue"] {
                font-size: 1.22rem;
            }
            .stock-card {
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 18px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
                height: 100%;
            }
            .header-card {
                background: linear-gradient(135deg, rgba(17, 91, 150, 0.14), rgba(30, 128, 90, 0.12)), var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 22px;
                box-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
            }
            .ticker-pill {
                display: inline-flex;
                gap: 8px;
                align-items: center;
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 5px 10px;
                color: var(--muted);
                font-size: 0.82rem;
                margin-right: 8px;
                margin-bottom: 8px;
            }
            .price-row {
                display: flex;
                align-items: end;
                flex-wrap: wrap;
                gap: 14px;
                margin-top: 10px;
            }
            .price {
                font-size: clamp(2rem, 5vw, 3.5rem);
                line-height: 1;
                font-weight: 760;
            }
            .gain { color: var(--gain); font-weight: 700; }
            .loss { color: var(--loss); font-weight: 700; }
            .muted { color: var(--muted); }
            .section-title {
                font-size: 1.08rem;
                font-weight: 720;
                margin: 1.35rem 0 0.65rem;
            }
            .logo-wrap img {
                width: 72px;
                height: 72px;
                object-fit: contain;
                border-radius: 8px;
                background: #fff;
                padding: 8px;
                border: 1px solid var(--border);
            }
            .stButton > button {
                height: 2.85rem;
                border-radius: 8px;
                font-weight: 720;
                width: 100%;
            }
            div[data-baseweb="select"] > div {
                border-radius: 8px;
            }
            .dataframe {
                border-radius: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_number(value: Any, currency: str | None = None, suffix: bool = True) -> str:
    if value is None or value == "" or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    prefix = f"{currency} " if currency else ""
    if not suffix:
        return f"{prefix}{number:,.2f}"
    abs_number = abs(number)
    for threshold, label in [(1e12, "T"), (1e9, "B"), (1e7, "Cr"), (1e5, "L"), (1e3, "K")]:
        if abs_number >= threshold:
            return f"{prefix}{number / threshold:,.2f}{label}"
    return f"{prefix}{number:,.2f}"


def format_percent(value: Any) -> str:
    if value is None or value == "" or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def normalize_symbol(query: str, preferred_exchange: str = "NSE") -> str:
    cleaned = query.strip()
    if not cleaned:
        return ""
    upper_query = cleaned.upper()

    for stock in INDIAN_STOCKS:
        values = {stock["name"].upper(), stock["nse"].upper(), stock["bse"].upper()}
        if upper_query in values:
            if preferred_exchange == "BSE":
                return f"{stock['bse']}.BO"
            return f"{stock['nse']}.NS"

    if upper_query.endswith((".NS", ".BO", ".BSE")):
        return upper_query.replace(".BSE", ".BO")

    if upper_query.isdigit():
        return f"{upper_query}.BO"

    return f"{upper_query}.NS" if preferred_exchange == "NSE" else f"{upper_query}.BO"


def stock_suggestions(search_text: str) -> list[str]:
    needle = search_text.strip().upper()
    suggestions: list[str] = []
    for stock in INDIAN_STOCKS:
        label = f"{stock['name']} | NSE: {stock['nse']} | BSE: {stock['bse']}"
        haystack = f"{stock['name']} {stock['nse']} {stock['bse']}".upper()
        if not needle or needle in haystack:
            suggestions.append(label)
    if needle and not suggestions:
        suggestions = [search_text.strip()]
    return suggestions[:12]


def symbol_from_suggestion(selection: str, typed_query: str, exchange: str) -> str:
    if "| NSE:" not in selection:
        return normalize_symbol(typed_query or selection, exchange)
    nse_part = selection.split("| NSE:", 1)[1].split("| BSE:", 1)[0].strip()
    bse_part = selection.split("| BSE:", 1)[1].strip()
    return f"{bse_part}.BO" if exchange == "BSE" else f"{nse_part}.NS"


@st.cache_data(ttl=900, show_spinner=False)
def get_ticker_info(symbol: str) -> dict[str, Any]:
    ticker = yf.Ticker(symbol)
    info = ticker.get_info()
    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        history = ticker.history(period="5d", interval="1d")
        if history.empty:
            raise ValueError(f"No Yahoo Finance data found for {symbol}.")
    return info


@st.cache_data(ttl=300, show_spinner=False)
def get_price_history(symbol: str, period: str, interval: str) -> pd.DataFrame:
    history = yf.Ticker(symbol).history(period=period, interval=interval, auto_adjust=False)
    if history.empty:
        return history
    history = history.reset_index()
    date_col = "Datetime" if "Datetime" in history.columns else "Date"
    history[date_col] = pd.to_datetime(history[date_col])
    return history


@st.cache_data(ttl=1800, show_spinner=False)
def get_financial_statements(symbol: str) -> dict[str, pd.DataFrame]:
    ticker = yf.Ticker(symbol)
    return {
        "Income Statement": clean_financial_statement(ticker.financials),
        "Balance Sheet": clean_financial_statement(ticker.balance_sheet),
        "Cash Flow": clean_financial_statement(ticker.cashflow),
    }


def clean_financial_statement(statement: pd.DataFrame) -> pd.DataFrame:
    if statement is None or statement.empty:
        return pd.DataFrame()
    cleaned = statement.copy()
    cleaned.columns = [pd.to_datetime(col).strftime("%Y") for col in cleaned.columns]
    cleaned.index = [str(idx).replace("_", " ") for idx in cleaned.index]
    return cleaned


def get_basic_info(info: dict[str, Any], symbol: str) -> dict[str, Any]:
    symbol_root = symbol.split(".", 1)[0]
    exchange_suffix = symbol.split(".", 1)[1] if "." in symbol else ""
    matched = next(
        (
            stock
            for stock in INDIAN_STOCKS
            if stock["nse"].upper() == symbol_root.upper() or stock["bse"].upper() == symbol_root.upper()
        ),
        None,
    )
    return {
        "NSE Symbol": matched["nse"] if matched else (symbol_root if exchange_suffix == "NS" else "N/A"),
        "BSE Symbol": matched["bse"] if matched else (symbol_root if exchange_suffix == "BO" else "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Industry": info.get("industry", "N/A"),
        "Country": info.get("country", "N/A"),
        "Website": info.get("website", "N/A"),
        "Employee Count": format_number(info.get("fullTimeEmployees"), suffix=False),
        "Founded Year": info.get("founded", "N/A"),
    }


def get_metric_values(info: dict[str, Any], history: pd.DataFrame, currency_symbol: str) -> dict[str, str]:
    latest_volume = None
    if not history.empty and "Volume" in history.columns:
        latest_volume = history["Volume"].dropna().iloc[-1] if not history["Volume"].dropna().empty else None
    return {
        "Market Capitalization": format_number(info.get("marketCap"), currency_symbol),
        "Enterprise Value": format_number(info.get("enterpriseValue"), currency_symbol),
        "Shares Outstanding": format_number(info.get("sharesOutstanding")),
        "P/E Ratio": format_number(info.get("trailingPE"), suffix=False),
        "Forward P/E": format_number(info.get("forwardPE"), suffix=False),
        "Price to Book": format_number(info.get("priceToBook"), suffix=False),
        "Dividend Yield": format_percent(info.get("dividendYield")),
        "Beta": format_number(info.get("beta"), suffix=False),
        "52 Week High": format_number(info.get("fiftyTwoWeekHigh"), currency_symbol, suffix=False),
        "52 Week Low": format_number(info.get("fiftyTwoWeekLow"), currency_symbol, suffix=False),
        "Average Volume": format_number(info.get("averageVolume")),
        "Current Volume": format_number(latest_volume),
    }


def statement_preview(statements: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = {
        "Revenue": ("Income Statement", "Total Revenue"),
        "Gross Profit": ("Income Statement", "Gross Profit"),
        "Operating Income": ("Income Statement", "Operating Income"),
        "Net Income": ("Income Statement", "Net Income"),
        "Total Assets": ("Balance Sheet", "Total Assets"),
        "Total Liabilities": ("Balance Sheet", "Total Liabilities Net Minority Interest"),
        "Shareholder Equity": ("Balance Sheet", "Stockholders Equity"),
        "Free Cash Flow": ("Cash Flow", "Free Cash Flow"),
    }
    data: dict[str, pd.Series] = {}
    for label, (statement_name, row_name) in rows.items():
        frame = statements.get(statement_name, pd.DataFrame())
        if not frame.empty and row_name in frame.index:
            data[label] = frame.loc[row_name]
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data).T


def build_price_chart(history: pd.DataFrame, title: str, currency_symbol: str) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28],
        specs=[[{"type": "candlestick"}], [{"type": "bar"}]],
    )
    if history.empty:
        return fig

    date_col = "Datetime" if "Datetime" in history.columns else "Date"
    colors = np.where(history["Close"] >= history["Open"], "#16803c", "#c43333")

    fig.add_trace(
        go.Candlestick(
            x=history[date_col],
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Price",
            increasing_line_color="#16803c",
            decreasing_line_color="#c43333",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=history[date_col],
            y=history["Volume"],
            marker_color=colors,
            name="Volume",
            opacity=0.52,
            hovertemplate="Volume: %{y:,.0f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    fig.update_layout(
        title=title,
        height=680,
        margin=dict(l=20, r=20, t=54, b=20),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title=f"Price ({currency_symbol})",
        yaxis2_title="Volume",
        template="plotly_white",
        dragmode="zoom",
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All"),
                ]
            )
        ),
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(127,127,127,0.16)")
    fig.update_xaxes(showgrid=False)
    return fig


def render_search() -> None:
    st.markdown("### Stock Research Dashboard")
    st.caption("Search Indian equities by company name, NSE symbol, or BSE code.")
    with st.container():
        col_query, col_suggest, col_exchange, col_button = st.columns([2.2, 3.4, 1.1, 0.9], vertical_alignment="bottom")
        with col_query:
            typed_query = st.text_input("Search", value=st.session_state.get("typed_query", ""), placeholder="Reliance, TCS, 500325")
        with col_suggest:
            suggestion = st.selectbox(
                "Autosuggest",
                stock_suggestions(typed_query),
                index=0,
                placeholder="Matching stocks",
            )
        with col_exchange:
            exchange = st.radio(
                "Exchange",
                ["NSE", "BSE"],
                index=0 if st.session_state.get("exchange", "NSE") == "NSE" else 1,
                horizontal=True,
            )
        with col_button:
            go_clicked = st.button("Go", type="primary")

    if go_clicked:
        symbol = symbol_from_suggestion(suggestion, typed_query, exchange or "NSE")
        st.session_state["symbol"] = symbol
        st.session_state["typed_query"] = typed_query
        st.session_state["exchange"] = exchange


def render_header(info: dict[str, Any], symbol: str, history: pd.DataFrame) -> None:
    currency_symbol = "₹" if info.get("currency") == "INR" or symbol.endswith((".NS", ".BO")) else info.get("financialCurrency", "")
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    previous_close = info.get("previousClose") or info.get("regularMarketPreviousClose")

    if (price is None or previous_close is None) and not history.empty:
        price = history["Close"].dropna().iloc[-1]
        previous_close = history["Close"].dropna().iloc[-2] if len(history["Close"].dropna()) > 1 else price

    change = (price - previous_close) if price is not None and previous_close is not None else None
    change_pct = (change / previous_close * 100) if change is not None and previous_close else None
    change_class = "gain" if change is not None and change >= 0 else "loss"
    change_text = (
        f"{format_number(change, currency_symbol, suffix=False)} ({change_pct:.2f}%)"
        if change is not None and change_pct is not None
        else "N/A"
    )
    logo_url = info.get("logo_url") or info.get("logoUrl")
    exchange_name = info.get("fullExchangeName") or info.get("exchange") or symbol
    company_name = info.get("longName") or info.get("shortName") or symbol

    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        st.markdown(
            f"""
            <div class="header-card">
                <span class="ticker-pill">{symbol}</span>
                <span class="ticker-pill">{exchange_name}</span>
                <h1 style="margin: 8px 0 4px; font-size: clamp(1.8rem, 4vw, 3.1rem);">{company_name}</h1>
                <div class="price-row">
                    <div class="price">{format_number(price, currency_symbol, suffix=False)}</div>
                    <div class="{change_class}">{change_text}</div>
                </div>
                <div class="muted" style="margin-top: 12px;">Last Updated: {datetime.now().strftime("%d %b %Y, %I:%M %p")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if logo_url:
            st.markdown(f'<div class="logo-wrap"><img src="{logo_url}" alt="{company_name} logo"></div>', unsafe_allow_html=True)


def render_basic_info(info: dict[str, Any], symbol: str) -> None:
    st.markdown('<div class="section-title">Basic Information</div>', unsafe_allow_html=True)
    basic = get_basic_info(info, symbol)
    cols = st.columns(4)
    for idx, (label, value) in enumerate(basic.items()):
        with cols[idx % 4]:
            if label == "Website" and value != "N/A":
                st.markdown(f'<div class="stock-card"><div class="muted">{label}</div><a href="{value}" target="_blank">{value}</a></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="stock-card"><div class="muted">{label}</div><strong>{value}</strong></div>', unsafe_allow_html=True)


def render_about(info: dict[str, Any]) -> None:
    st.markdown('<div class="section-title">About Company</div>', unsafe_allow_html=True)
    summary = info.get("longBusinessSummary") or "No business summary is available from Yahoo Finance for this company."
    if len(summary) > 520:
        st.write(summary[:520].rsplit(" ", 1)[0] + "...")
        with st.expander("Read More"):
            st.write(summary)
    else:
        st.write(summary)


def render_metrics(info: dict[str, Any], history: pd.DataFrame, symbol: str) -> None:
    st.markdown('<div class="section-title">Key Metrics / Overview</div>', unsafe_allow_html=True)
    currency_symbol = "₹" if info.get("currency") == "INR" or symbol.endswith((".NS", ".BO")) else info.get("financialCurrency", "")
    metrics = get_metric_values(info, history, currency_symbol)
    cols = st.columns(4)
    for idx, (label, value) in enumerate(metrics.items()):
        with cols[idx % 4]:
            st.metric(label, value)


def render_financials(symbol: str) -> None:
    st.markdown('<div class="section-title">Financials</div>', unsafe_allow_html=True)
    statements = get_financial_statements(symbol)
    overview = statement_preview(statements)
    if not overview.empty:
        st.dataframe(overview.applymap(lambda value: format_number(value, "₹")), use_container_width=True)

    tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
    for tab, statement_name in zip(tabs, ["Income Statement", "Balance Sheet", "Cash Flow"]):
        with tab:
            frame = statements.get(statement_name, pd.DataFrame())
            if frame.empty:
                st.info(f"{statement_name} is not available from Yahoo Finance for this symbol.")
                continue
            st.dataframe(frame.applymap(lambda value: format_number(value, "₹")), use_container_width=True)
            csv = frame.to_csv().encode("utf-8")
            st.download_button(
                f"Download {statement_name} CSV",
                data=csv,
                file_name=f"{symbol}_{statement_name.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )


def render_chart(symbol: str, company_name: str) -> None:
    st.markdown('<div class="section-title">Price Chart</div>', unsafe_allow_html=True)
    period_options = list(PERIOD_CONFIG.keys())
    period = st.radio("Time Period", period_options, index=period_options.index("1Y"), horizontal=True)
    config = PERIOD_CONFIG[period]
    history = get_price_history(symbol, config["period"], config["interval"])
    if history.empty:
        st.warning("No historical price data is available for this period.")
        return
    fig = build_price_chart(history, f"{company_name} Price and Volume", "₹")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True})


def render_dashboard(symbol: str) -> None:
    try:
        with st.spinner("Fetching live market data from Yahoo Finance..."):
            info = get_ticker_info(symbol)
            daily_history = get_price_history(symbol, "5d", "1d")
    except Exception as exc:
        st.error(f"Could not load data for `{symbol}`. Check the symbol and try again. Details: {exc}")
        return

    company_name = info.get("longName") or info.get("shortName") or symbol
    render_header(info, symbol, daily_history)
    render_basic_info(info, symbol)
    render_about(info)
    render_metrics(info, daily_history, symbol)
    render_financials(symbol)
    render_chart(symbol, company_name)


def main() -> None:
    apply_theme()
    if "symbol" not in st.session_state:
        st.session_state["symbol"] = "RELIANCE.NS"
    if "exchange" not in st.session_state:
        st.session_state["exchange"] = "NSE"

    render_search()
    st.divider()
    render_dashboard(st.session_state["symbol"])


if __name__ == "__main__":
    main()
