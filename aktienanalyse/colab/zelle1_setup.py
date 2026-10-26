# ============================================================
# ZELLE 1: SETUP – Bibliotheken installieren
# ============================================================
# Diese Zelle muss nur EINMAL pro Colab-Sitzung ausgeführt werden.
#   yfinance  -> lädt Aktienkurse kostenlos von Yahoo Finance
#   plotly    -> zeichnet interaktive Charts (zoomen, Maus darüber halten)
#   pandas-ta -> berechnet technische Indikatoren (SMA, RSI, MACD)
# Das "-q" sorgt nur dafür, dass die Installation weniger Text ausgibt.
#
# pandas-ta wird mit "--no-deps" installiert: So bleiben die in Colab bereits
# vorhandenen Grundbibliotheken (numpy, numba) unverändert. Würde pip sie
# austauschen, passen sie nicht mehr zur laufenden Sitzung und es kommt zu
# Fehlern wie "'numpy.ufunc' object has no attribute '__module__'".
#
# Falls dieser Fehler trotzdem auftritt: Menü "Laufzeit" -> "Sitzung neu starten",
# danach Zelle 1 NICHT erneut ausführen, sondern direkt mit Zelle 2 weitermachen.

!pip install -q yfinance plotly
!pip install -q --no-deps pandas-ta

print("✅ Installation abgeschlossen. Weiter mit Zelle 2.")
