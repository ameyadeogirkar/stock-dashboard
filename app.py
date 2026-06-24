
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
