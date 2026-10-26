# ============================================================
# ZELLE 1: SETUP – Bibliotheken installieren
# ============================================================
# Diese Zelle muss nur EINMAL pro Colab-Sitzung ausgeführt werden.
#   yfinance  -> lädt Aktienkurse kostenlos von Yahoo Finance
#   plotly    -> zeichnet interaktive Charts (zoomen, Maus darüber halten)
#   pandas-ta -> berechnet technische Indikatoren (SMA, RSI, MACD)
# Das "-q" sorgt nur dafür, dass die Installation weniger Text ausgibt.

!pip install -q yfinance plotly pandas-ta

print("✅ Installation abgeschlossen. Weiter mit Zelle 2.")
