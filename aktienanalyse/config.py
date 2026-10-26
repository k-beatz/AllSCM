"""Zentrale Einstellungen: Gewichte, Schwellenwerte und Indikator-Parameter.

Hier kann man Werte anpassen, ohne den restlichen Code anzufassen.
"""

# --- Kursdaten ---
# Zeiträume, die man in der Oberfläche auswählen kann (Schlüssel = yfinance-Kürzel)
PERIODS = {
    "6mo": "6 Monate",
    "1y": "1 Jahr",
    "2y": "2 Jahre",
    "5y": "5 Jahre",
}
DEFAULT_PERIOD = "1y"

# Für die Indikatoren (v. a. SMA200) laden wir immer mindestens so viel Historie,
# auch wenn im Chart nur ein kürzerer Zeitraum angezeigt wird.
MIN_CALC_PERIOD = "2y"

# --- Indikator-Einstellungen ---
SMA_SHORT = 50
SMA_LONG = 200
RSI_PERIOD = 14
RSI_OVERSOLD = 30      # darunter: überverkauft -> positiv
RSI_OVERBOUGHT = 70    # darüber: überkauft -> negativ
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD = 2.0
# "Am Band" heißt: Kurs liegt in den unteren/oberen 5 % der Bandbreite (oder außerhalb)
BB_TOUCH_TOLERANCE = 0.05

# --- Gewichte der Teilsignale im Chart-Score (Summe = 1) ---
TECHNICAL_WEIGHTS = {
    "trend": 0.40,
    "macd": 0.25,
    "rsi": 0.20,
    "bollinger": 0.15,
}

# --- Schwellenwerte für die Empfehlung ---
BUY_THRESHOLD = 0.3     # Score darüber -> Kaufen
SELL_THRESHOLD = -0.3   # Score darunter -> Verkaufen
