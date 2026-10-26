"""Kursdaten holen.

Es gibt eine kleine Schnittstelle (PriceSource) und eine Umsetzung für yfinance.
So kann man später einen anderen Datenanbieter anschließen, ohne den Rest zu ändern.
"""

from abc import ABC, abstractmethod

import pandas as pd
import yfinance as yf

# Diese Spalten liefert jede Kursquelle zurück
PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


class PriceDataError(Exception):
    """Fehler beim Laden von Kursdaten, mit einer verständlichen Meldung für die Oberfläche."""


class PriceSource(ABC):
    """Schnittstelle für alle Kursdaten-Anbieter."""

    @abstractmethod
    def get_prices(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Liefert Tagesdaten: Index = Datum, Spalten = Open, High, Low, Close, Volume."""


class YFinancePriceSource(PriceSource):
    """Kursdaten von Yahoo Finance über die Bibliothek yfinance (kostenlos)."""

    def get_prices(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Lädt Tagesdaten für ein Kürzel und bereitet sie einheitlich auf."""
        ticker = ticker.strip().upper()
        if not ticker:
            raise PriceDataError("Bitte ein Aktienkürzel eingeben, z. B. AAPL oder SAP.DE.")

        try:
            raw = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
        except Exception as exc:  # z. B. keine Internetverbindung
            raise PriceDataError(
                f"Kursdaten für „{ticker}“ konnten nicht geladen werden. "
                f"Besteht eine Internetverbindung? (Details: {exc})"
            ) from exc

        if raw is None or raw.empty:
            raise PriceDataError(
                f"Für „{ticker}“ wurden keine Kursdaten gefunden. "
                "Ist das Kürzel richtig? Deutsche Aktien brauchen meist die Endung .DE (z. B. SAP.DE)."
            )

        return _clean(raw)


def _clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Behält nur die benötigten Spalten und entfernt die Zeitzone aus dem Datum."""
    df = raw[PRICE_COLUMNS].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df.index.name = "Datum"
    return df.dropna(subset=["Close"])


# Standard-Anbieter der Anwendung
_default_source: PriceSource = YFinancePriceSource()


def get_prices(ticker: str, period: str = "1y", source: PriceSource | None = None) -> pd.DataFrame:
    """Bequeme Abkürzung: Kursdaten vom Standard-Anbieter (oder einem übergebenen) holen."""
    return (source or _default_source).get_prices(ticker, period)
