"""Einfache Tests für die Chart-Analyse (Start: pytest)."""

import numpy as np
import pandas as pd
import pytest

from analysis import technical


def make_prices(closes) -> pd.DataFrame:
    """Erzeugt künstliche Kursdaten aus einer Liste von Schlusskursen."""
    closes = pd.Series(closes, dtype=float)
    index = pd.bdate_range("2024-01-01", periods=len(closes))
    return pd.DataFrame({"Open": closes.values, "High": closes.values + 1,
                         "Low": closes.values - 1, "Close": closes.values,
                         "Volume": 1000}, index=index)


def test_sma_rechnet_mittelwert():
    close = pd.Series([1, 2, 3, 4, 5], dtype=float)
    result = technical.sma(close, 3)
    assert pd.isna(result.iloc[1])
    assert result.iloc[-1] == 4.0


def test_rsi_steigende_kurse_ist_hoch():
    close = pd.Series(np.arange(1, 50), dtype=float)
    assert technical.rsi(close, 14).iloc[-1] == 100.0


def test_rsi_fallende_kurse_ist_niedrig():
    close = pd.Series(np.arange(50, 1, -1), dtype=float)
    assert technical.rsi(close, 14).iloc[-1] == pytest.approx(0.0)


def test_trend_signal():
    assert technical.trend_signal(110, 105, 100)[0] == 1.0
    assert technical.trend_signal(90, 95, 100)[0] == -1.0
    assert technical.trend_signal(110, 95, 100)[0] == 0.0
    assert technical.trend_signal(110, float("nan"), float("nan"))[0] == 0.0


def test_rsi_signal():
    assert technical.rsi_signal(25)[0] == 1.0
    assert technical.rsi_signal(75)[0] == -1.0
    assert technical.rsi_signal(50)[0] == 0.0


def test_macd_signal():
    assert technical.macd_signal(1.0, 0.5)[0] == 1.0
    assert technical.macd_signal(0.5, 1.0)[0] == -1.0


def test_bollinger_signal():
    assert technical.bollinger_signal(90, 90, 110)[0] == 1.0   # am unteren Band
    assert technical.bollinger_signal(111, 90, 110)[0] == -1.0  # über dem oberen Band
    assert technical.bollinger_signal(100, 90, 110)[0] == 0.0   # in der Mitte


def test_weighted_score():
    signals = [
        technical.Signal("a", "A", "", 1.0, 0.4, ""),
        technical.Signal("b", "B", "", -1.0, 0.2, ""),
        technical.Signal("c", "C", "", 0.0, 0.4, ""),
    ]
    assert technical.weighted_score(signals) == pytest.approx(0.2)


def test_analyze_aufwaertstrend_ist_positiv():
    # Stetig steigende Kurse über 300 Tage: Trend und MACD positiv
    data = technical.add_indicators(make_prices(np.linspace(100, 200, 300)))
    result = technical.analyze(data)
    signals = {s.key: s.signal for s in result.signals}
    assert signals["trend"] == 1.0
    assert signals["macd"] == 1.0
    assert -1.0 <= result.score <= 1.0
    assert result.score > 0


def test_analyze_mit_kurzer_historie_ist_trend_neutral():
    data = technical.add_indicators(make_prices(np.linspace(100, 120, 60)))
    result = technical.analyze(data)
    assert {s.key: s.signal for s in result.signals}["trend"] == 0.0
