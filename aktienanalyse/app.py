"""Streamlit-Oberfläche der Aktienanalyse.

Start:  streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import config
from analysis import decision, technical
from data.prices import PriceDataError, get_prices

# Farben für die Empfehlung
COLORS = {decision.BUY: "#1a9850", decision.HOLD: "#7f7f7f", decision.SELL: "#d73027"}

# Reihenfolge der Zeiträume, um den längeren von zwei zu bestimmen
PERIOD_ORDER = list(config.PERIODS)


@st.cache_data(ttl=3600, show_spinner=False)
def load_prices(ticker: str, period: str) -> pd.DataFrame:
    """Kursdaten laden und eine Stunde lang zwischenspeichern."""
    return get_prices(ticker, period)


def calc_period(display_period: str) -> str:
    """Für die Indikatoren mindestens MIN_CALC_PERIOD laden (wegen SMA200)."""
    return max(display_period, config.MIN_CALC_PERIOD, key=PERIOD_ORDER.index)


def cut_to_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Schneidet die Daten auf den gewählten Anzeigezeitraum zu."""
    offsets = {"6mo": pd.DateOffset(months=6), "1y": pd.DateOffset(years=1),
               "2y": pd.DateOffset(years=2), "5y": pd.DateOffset(years=5)}
    start = df.index[-1] - offsets[period]
    return df[df.index >= start]


def build_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """Kerzenchart mit SMA50/200 und Bollinger-Bändern, darunter RSI und MACD."""
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                        row_heights=[0.6, 0.2, 0.2],
                        subplot_titles=(f"{ticker} – Kurs", "RSI (14)", "MACD (12/26/9)"))

    # Oberes Diagramm: Kerzen, Durchschnitte, Bollinger-Bänder
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="Kurs"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Oben"], name="Bollinger oben",
                             line=dict(color="rgba(120,120,200,0.6)", width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_Unten"], name="Bollinger unten",
                             line=dict(color="rgba(120,120,200,0.6)", width=1),
                             fill="tonexty", fillcolor="rgba(120,120,200,0.08)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50",
                             line=dict(color="#ff7f0e", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA200"], name="SMA200",
                             line=dict(color="#1f77b4", width=1.5)), row=1, col=1)

    # Mitte: RSI mit Linien bei 30 und 70
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI",
                             line=dict(color="#9467bd", width=1.5)), row=2, col=1)
    fig.add_hline(y=config.RSI_OVERBOUGHT, line_dash="dot", line_color="#d73027", row=2, col=1)
    fig.add_hline(y=config.RSI_OVERSOLD, line_dash="dot", line_color="#1a9850", row=2, col=1)

    # Unten: MACD, Signallinie und Histogramm
    hist_colors = ["#1a9850" if v >= 0 else "#d73027" for v in df["MACD_Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_Hist"], name="Histogramm",
                         marker_color=hist_colors, opacity=0.5), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD",
                             line=dict(color="#1f77b4", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], name="Signallinie",
                             line=dict(color="#ff7f0e", width=1.5)), row=3, col=1)

    fig.update_layout(height=800, xaxis_rangeslider_visible=False, hovermode="x unified",
                      legend=dict(orientation="h", y=1.08, x=0), margin=dict(t=110, b=20))
    fig.update_yaxes(range=[0, 100], row=2, col=1)
    # Wochenenden ausblenden, damit keine Lücken entstehen
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    return fig


def signal_table(signals: list[technical.Signal]) -> pd.DataFrame:
    """Teilsignale als Tabelle für die Anzeige."""
    labels = {1.0: "🟢 positiv (+1)", 0.0: "⚪ neutral (0)", -1.0: "🔴 negativ (−1)"}
    return pd.DataFrame([
        {"Indikator": s.name, "Wert": s.value, "Teilsignal": labels.get(s.signal, s.signal),
         "Gewicht": f"{s.weight:.0%}", "Begründung": s.reason}
        for s in signals
    ])


def show_recommendation(result: decision.Decision) -> None:
    """Zeigt die Empfehlung groß und farbig an."""
    color = COLORS[result.recommendation]
    st.markdown(
        f"<div style='padding:1rem 1.5rem;border-radius:0.6rem;background:{color};color:white'>"
        f"<div style='font-size:0.9rem;opacity:0.9'>Vorläufige Empfehlung (nur Chart-Analyse)</div>"
        f"<div style='font-size:2.6rem;font-weight:700;line-height:1.2'>{result.recommendation}</div>"
        f"<div style='font-size:1.1rem'>Gesamtscore: {result.total_score:+.2f}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.write(result.reason)


# ---------------------------------------------------------------------------
# Seitenaufbau
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Aktienanalyse", page_icon="📈", layout="wide")
st.title("📈 Aktienanalyse")
st.caption("Phase 1: Chart-Analyse mit technischen Indikatoren")

# 1. Eingabe
with st.form("eingabe"):
    col1, col2, col3 = st.columns([2, 1, 1])
    ticker_input = col1.text_input("Aktienkürzel", value="AAPL",
                                   help="Beispiele: AAPL (Apple), MSFT, SAP.DE, BMW.DE")
    period = col2.selectbox("Zeitraum", options=list(config.PERIODS),
                            index=PERIOD_ORDER.index(config.DEFAULT_PERIOD),
                            format_func=config.PERIODS.get)
    col3.write("")  # Abstand, damit der Button auf einer Höhe mit den Feldern steht
    submitted = col3.form_submit_button("Analysieren", type="primary", width="stretch")

# Gewählte Werte merken, damit die Anzeige beim Umschalten erhalten bleibt
if submitted:
    st.session_state["ticker"] = ticker_input.strip().upper()
    st.session_state["period"] = period

if "ticker" not in st.session_state:
    st.info("Kürzel eingeben und auf „Analysieren“ klicken.")
else:
    ticker = st.session_state["ticker"]
    period = st.session_state["period"]
    try:
        with st.spinner(f"Lade Kursdaten für {ticker} …"):
            prices = load_prices(ticker, calc_period(period))
    except PriceDataError as err:
        st.error(str(err))
    else:
        data = technical.add_indicators(prices)
        result = decision.decide(technical.analyze(data))

        # 2. Empfehlung
        show_recommendation(result)

        # 3. Chart
        st.subheader("Chart")
        st.plotly_chart(build_chart(cut_to_period(data, period), ticker), width="stretch")
        st.caption(f"Letzter Handelstag: {data.index[-1]:%d.%m.%Y}")

        # 4. Teilsignale
        st.subheader("Teilsignale")
        st.dataframe(signal_table(result.signals), hide_index=True, width="stretch")
        st.caption("Chart-Score = gewichteter Mittelwert der Teilsignale (von −1 bis +1).")

# Fußzeile
st.divider()
st.warning("⚠️ **Keine Anlageberatung.** Diese Software ist ein Lern- und Experimentierwerkzeug. "
           "Sie führt keine echten Orders aus.")
