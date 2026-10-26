# ============================================================
# ZELLE 3: AUSFÜHRUNG UND INTERAKTION
# ============================================================
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ---------- 1) HIER DAS AKTIENKÜRZEL EINTRAGEN ----------
# Beispiele: "AAPL" (Apple), "MSFT" (Microsoft), "SAP.DE" (SAP in Xetra), "BMW.DE", "TSLA"
# Deutsche Aktien bekommen bei Yahoo Finance meist die Endung ".DE".
TICKER = "AAPL"

# ---------- 2) DATEN LADEN UND ANALYSIEREN ----------
daten = lade_kursdaten(TICKER)
daten = berechne_indikatoren(daten)
ergebnis = erzeuge_signal(daten)

# ---------- 3) INTERAKTIVEN CHART ZEICHNEN ----------
# Drei Bereiche untereinander: Kerzenchart mit SMAs, RSI, MACD
fig = make_subplots(
    rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
    row_heights=[0.6, 0.2, 0.2],
    subplot_titles=(f"{TICKER} – Kurs mit SMA50 / SMA200", "RSI (14)", "MACD (12, 26, 9)"),
)

# Oben: Kerzen (grün = Tag gestiegen, rot = Tag gefallen) und Durchschnittslinien
fig.add_trace(go.Candlestick(x=daten.index, open=daten["Open"], high=daten["High"],
                             low=daten["Low"], close=daten["Close"], name="Kurs"), row=1, col=1)
fig.add_trace(go.Scatter(x=daten.index, y=daten["SMA50"], name="SMA50", line=dict(color="orange", width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=daten.index, y=daten["SMA200"], name="SMA200", line=dict(color="royalblue", width=1.5)), row=1, col=1)

# Mitte: RSI mit den Grenzlinien 30 und 70
fig.add_trace(go.Scatter(x=daten.index, y=daten["RSI"], name="RSI", line=dict(color="purple", width=1.5)), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Unten: MACD-Linie, Signallinie und Histogramm (Balken)
balkenfarben = ["green" if wert >= 0 else "red" for wert in daten["MACD_Hist"].fillna(0)]
fig.add_trace(go.Bar(x=daten.index, y=daten["MACD_Hist"], name="MACD-Histogramm", marker_color=balkenfarben), row=3, col=1)
fig.add_trace(go.Scatter(x=daten.index, y=daten["MACD"], name="MACD", line=dict(color="black", width=1.2)), row=3, col=1)
fig.add_trace(go.Scatter(x=daten.index, y=daten["MACD_Signal"], name="Signallinie", line=dict(color="orange", width=1.2)), row=3, col=1)

fig.update_layout(height=850, xaxis_rangeslider_visible=False, hovermode="x unified",
                  legend=dict(orientation="h", y=1.04))
fig.update_yaxes(range=[0, 100], row=2, col=1)
fig.show()

# ---------- 4) HANDELSSIGNAL ALS TEXT ----------
symbole = {"KAUFEN": "🟢", "HALTEN": "🟡", "VERKAUFEN": "🔴"}
print("=" * 70)
print(f"{symbole[ergebnis['signal']]} SIGNAL für {TICKER}: {ergebnis['signal']}")
print("=" * 70)
print(ergebnis["begruendung"])
if "datum" in ergebnis:
    print(f"\nStand {ergebnis['datum']}: Schluss {ergebnis['schlusskurs']:.2f} | "
          f"SMA50 {ergebnis['sma50']:.2f} | SMA200 {ergebnis['sma200']:.2f} | "
          f"RSI {ergebnis['rsi']:.1f} | MACD {ergebnis['macd']:.2f} / Signal {ergebnis['macd_signal']:.2f}")
print("Hinweis: Das ist eine regelbasierte Übung und keine Anlageberatung.\n")

# ---------- 5) PAPER-TRADING ----------
# Das Depot wird nur beim ERSTEN Ausführen angelegt. So bleiben Ihre Käufe
# erhalten, wenn Sie diese Zelle erneut starten (z. B. mit einem anderen TICKER).
# Neu beginnen mit 10.000 €:  portfolio = Portfolio()
if "portfolio" not in globals():
    portfolio = Portfolio()

# So handeln Sie – das "#" am Zeilenanfang entfernen und die Zelle erneut ausführen.
# (Achtung: Jedes erneute Ausführen führt die Order noch einmal aus!)
# Bequemer: eine neue Zelle anlegen (+ Code) und den Befehl dort eintippen.
#
# portfolio.buy('AAPL', 10)        # 10 Apple-Aktien kaufen
# portfolio.sell('AAPL', 5)        # 5 Apple-Aktien verkaufen
# portfolio.buy(TICKER, 3)         # 3 Stück der oben analysierten Aktie kaufen
#
# Automatisch nach Signal handeln (optional):
# if ergebnis["signal"] == "KAUFEN":
#     portfolio.buy(TICKER, 5)
# elif ergebnis["signal"] == "VERKAUFEN" and TICKER in portfolio.positionen_daten:
#     portfolio.sell(TICKER, portfolio.positionen_daten[TICKER]["anzahl"])

# Kontostand, Positionen und Historie anzeigen
portfolio.kontostand()
print("\n📊 Offene Positionen:")
display(portfolio.positionen() if portfolio.positionen_daten else "Noch keine Positionen.")
print("\n📜 Transaktionshistorie:")
display(portfolio.historie() if portfolio.transaktionen else "Noch keine Transaktionen.")
