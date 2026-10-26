"""Chart-Analyse: Indikatoren berechnen und in einen Chart-Score übersetzen.

Die Indikatoren werden direkt mit pandas berechnet (ohne pandas-ta),
damit die Installation auch unter Windows mit Python 3.11 problemlos klappt.

Jedes Teilsignal ist +1 (positiv), 0 (neutral) oder -1 (negativ).
Der Chart-Score ist der gewichtete Mittelwert und liegt zwischen -1 und +1.
"""

from dataclasses import dataclass

import pandas as pd

import config


@dataclass
class Signal:
    """Ein Teilsignal mit Wert, Bewertung, Gewicht und Erklärung in Worten."""

    key: str          # interner Name, z. B. "rsi"
    name: str         # Anzeigename, z. B. "RSI (14)"
    value: str        # aktueller Wert als Text
    signal: float     # -1, 0 oder +1
    weight: float     # Gewicht im Chart-Score
    reason: str       # kurze Begründung


@dataclass
class TechnicalResult:
    """Ergebnis der Chart-Analyse."""

    score: float
    signals: list[Signal]


# ---------------------------------------------------------------------------
# Indikatoren berechnen
# ---------------------------------------------------------------------------

def sma(close: pd.Series, window: int) -> pd.Series:
    """Einfacher gleitender Durchschnitt über `window` Tage."""
    return close.rolling(window=window, min_periods=window).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Relative Stärke (RSI) nach Wilder, Werte von 0 bis 100."""
    diff = close.diff()
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss
    result = 100 - 100 / (1 + rs)
    # Nur Gewinne, keine Verluste -> RSI 100
    return result.where(avg_loss != 0, 100.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """MACD-Linie, Signallinie und Histogramm."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame(
        {"MACD": macd_line, "MACD_Signal": signal_line, "MACD_Hist": macd_line - signal_line}
    )


def bollinger(close: pd.Series, period: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Bollinger-Bänder: Mittellinie und oberes/unteres Band."""
    middle = sma(close, period)
    std = close.rolling(window=period, min_periods=period).std(ddof=0)
    return pd.DataFrame(
        {"BB_Mitte": middle, "BB_Oben": middle + num_std * std, "BB_Unten": middle - num_std * std}
    )


def add_indicators(prices: pd.DataFrame) -> pd.DataFrame:
    """Hängt alle Indikatoren als neue Spalten an eine Kopie der Kursdaten an."""
    df = prices.copy()
    close = df["Close"]
    df["SMA50"] = sma(close, config.SMA_SHORT)
    df["SMA200"] = sma(close, config.SMA_LONG)
    df["RSI"] = rsi(close, config.RSI_PERIOD)
    df = df.join(macd(close, config.MACD_FAST, config.MACD_SLOW, config.MACD_SIGNAL))
    df = df.join(bollinger(close, config.BB_PERIOD, config.BB_STD))
    return df


# ---------------------------------------------------------------------------
# Indikatoren in Teilsignale übersetzen
# ---------------------------------------------------------------------------

def trend_signal(close: float, sma50: float, sma200: float) -> tuple[float, str]:
    """Trend über gleitende Durchschnitte: Kurs und SMA50 im Vergleich zum SMA200."""
    if pd.isna(sma50) or pd.isna(sma200):
        return 0.0, "Zu wenig Historie für SMA200 – neutral gewertet."
    if close > sma200 and sma50 > sma200:
        return 1.0, "Kurs und SMA50 liegen über dem SMA200 – Aufwärtstrend."
    if close < sma200 and sma50 < sma200:
        return -1.0, "Kurs und SMA50 liegen unter dem SMA200 – Abwärtstrend."
    return 0.0, "Gemischtes Bild der Durchschnitte – kein klarer Trend."


def rsi_signal(rsi_value: float) -> tuple[float, str]:
    """RSI: unter 30 überverkauft (positiv), über 70 überkauft (negativ)."""
    if pd.isna(rsi_value):
        return 0.0, "RSI nicht berechenbar – neutral gewertet."
    if rsi_value < config.RSI_OVERSOLD:
        return 1.0, f"RSI unter {config.RSI_OVERSOLD} – überverkauft, Erholung möglich."
    if rsi_value > config.RSI_OVERBOUGHT:
        return -1.0, f"RSI über {config.RSI_OVERBOUGHT} – überkauft, Rücksetzer möglich."
    return 0.0, "RSI im neutralen Bereich."


def macd_signal(macd_value: float, signal_value: float) -> tuple[float, str]:
    """MACD: über der Signallinie positiv, darunter negativ."""
    if pd.isna(macd_value) or pd.isna(signal_value):
        return 0.0, "MACD nicht berechenbar – neutral gewertet."
    if macd_value > signal_value:
        return 1.0, "MACD liegt über der Signallinie – Schwung nach oben."
    if macd_value < signal_value:
        return -1.0, "MACD liegt unter der Signallinie – Schwung nach unten."
    return 0.0, "MACD gleich Signallinie – neutral."


def bollinger_signal(close: float, lower: float, upper: float) -> tuple[float, str]:
    """Bollinger: Kurs am unteren Band positiv, am oberen Band negativ."""
    if pd.isna(lower) or pd.isna(upper) or upper == lower:
        return 0.0, "Bollinger-Bänder nicht berechenbar – neutral gewertet."
    position = (close - lower) / (upper - lower)  # 0 = unteres Band, 1 = oberes Band
    if position <= config.BB_TOUCH_TOLERANCE:
        return 1.0, "Kurs am unteren Bollinger-Band – relativ günstig."
    if position >= 1 - config.BB_TOUCH_TOLERANCE:
        return -1.0, "Kurs am oberen Bollinger-Band – relativ teuer."
    return 0.0, "Kurs innerhalb der Bollinger-Bänder."


def weighted_score(signals: list[Signal]) -> float:
    """Gewichteter Mittelwert der Teilsignale (Ergebnis zwischen -1 und +1)."""
    total_weight = sum(s.weight for s in signals)
    if total_weight == 0:
        return 0.0
    return sum(s.signal * s.weight for s in signals) / total_weight


def analyze(df: pd.DataFrame, weights: dict[str, float] | None = None) -> TechnicalResult:
    """Bewertet den letzten Handelstag. `df` muss die Spalten aus add_indicators() haben."""
    weights = weights or config.TECHNICAL_WEIGHTS
    last = df.iloc[-1]
    close = last["Close"]

    trend, trend_reason = trend_signal(close, last["SMA50"], last["SMA200"])
    rsi_s, rsi_reason = rsi_signal(last["RSI"])
    macd_s, macd_reason = macd_signal(last["MACD"], last["MACD_Signal"])
    bb_s, bb_reason = bollinger_signal(close, last["BB_Unten"], last["BB_Oben"])

    signals = [
        Signal("trend", f"Trend (SMA{config.SMA_SHORT}/{config.SMA_LONG})",
               f"Kurs {close:.2f} · SMA50 {_fmt(last['SMA50'])} · SMA200 {_fmt(last['SMA200'])}",
               trend, weights["trend"], trend_reason),
        Signal("macd", f"MACD ({config.MACD_FAST}/{config.MACD_SLOW}/{config.MACD_SIGNAL})",
               f"MACD {_fmt(last['MACD'])} · Signal {_fmt(last['MACD_Signal'])}",
               macd_s, weights["macd"], macd_reason),
        Signal("rsi", f"RSI ({config.RSI_PERIOD})", _fmt(last["RSI"], 1),
               rsi_s, weights["rsi"], rsi_reason),
        Signal("bollinger", f"Bollinger ({config.BB_PERIOD}, {config.BB_STD:g} σ)",
               f"Unten {_fmt(last['BB_Unten'])} · Oben {_fmt(last['BB_Oben'])}",
               bb_s, weights["bollinger"], bb_reason),
    ]
    return TechnicalResult(score=weighted_score(signals), signals=signals)


def _fmt(value: float, digits: int = 2) -> str:
    """Zahl als Text, oder „–“ wenn sie fehlt."""
    return "–" if pd.isna(value) else f"{value:.{digits}f}"
