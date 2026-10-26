# ============================================================
# ZELLE 2: ENGINE UND BROKER
# ============================================================
# Diese Zelle erstellt nur die "Werkzeuge" (Klassen und Funktionen).
# Sie handelt noch nichts und lädt noch keine Charts.
# Benutzt werden die Werkzeuge in Zelle 3.

import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import yfinance as yf

# pandas-ta laden. Falls das in Ihrer Colab-Version nicht klappt,
# rechnet das Programm die Indikatoren einfach selbst (gleiche Formeln).
try:
    import pandas_ta as ta
    PANDAS_TA_VERFUEGBAR = True
except Exception:
    PANDAS_TA_VERFUEGBAR = False
    print("⚠️ pandas-ta konnte nicht geladen werden – es wird die eingebaute Ersatzberechnung genutzt.")


def euro(betrag):
    """Formatiert eine Zahl als Euro-Betrag im deutschen Format, z. B. 10.000,00 €."""
    text = f"{betrag:,.2f}"                                   # 10,000.00
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")  # 10.000,00
    return f"{text} €"


# ------------------------------------------------------------
# TEIL A: KURSE IN ECHTZEIT HOLEN (inkl. Umrechnung in Euro)
# ------------------------------------------------------------

def hole_wechselkurs(waehrung):
    """
    Liefert, wie viele Einheiten der Fremdwährung 1 Euro kostet.
    Beispiel: hole_wechselkurs("USD") -> ca. 1,08 (1 € = 1,08 $).
    Für Euro-Aktien ist der Kurs einfach 1.
    """
    if waehrung == "EUR":
        return 1.0
    daten = yf.Ticker(f"EUR{waehrung}=X").history(period="5d")
    if daten.empty:
        raise ValueError(f"Wechselkurs EUR/{waehrung} konnte nicht geladen werden.")
    return float(daten["Close"].iloc[-1])


def hole_aktuellen_kurs(symbol):
    """
    Holt den aktuellen Kurs einer Aktie von Yahoo Finance und rechnet ihn in Euro um.
    Rückgabe: (Kurs in Euro, Kurs in Originalwährung, Originalwährung)
    """
    ticker = yf.Ticker(symbol)
    kurs, waehrung = None, None

    # 1. Versuch: der schnelle "Echtzeit"-Kurs
    try:
        kurs = float(ticker.fast_info["last_price"])
        waehrung = ticker.fast_info["currency"]
    except Exception:
        pass

    # 2. Versuch (Rückfallebene): letzter Schlusskurs der vergangenen Tage
    if kurs is None or np.isnan(kurs) or kurs <= 0:
        daten = ticker.history(period="5d")
        if daten.empty:
            raise ValueError(f"Für '{symbol}' wurden keine Kurse gefunden. Ist das Kürzel richtig?")
        kurs = float(daten["Close"].iloc[-1])

    waehrung = (waehrung or "USD")
    # Britische Aktien werden in Pence (GBp) notiert -> in Pfund umrechnen
    if waehrung in ("GBp", "GBX"):
        kurs, waehrung = kurs / 100, "GBP"
    waehrung = waehrung.upper()

    kurs_eur = kurs / hole_wechselkurs(waehrung)
    return kurs_eur, kurs, waehrung


# ------------------------------------------------------------
# TEIL B: DAS PORTFOLIO (der virtuelle Broker)
# ------------------------------------------------------------

class Portfolio:
    """
    Ein virtuelles Depot zum Üben (Paper-Trading) – es wird kein echtes Geld bewegt.
      - Startkapital: 10.000 €
      - Gebühr: 0,1 % vom Ordervolumen bei jedem Kauf und Verkauf
      - Alle Kurse werden in Euro umgerechnet
      - Jede Transaktion wird in der Historie gespeichert
    """

    def __init__(self, startkapital=10_000.0, gebuehr_prozent=0.1):
        self.startkapital = float(startkapital)
        self.bargeld = float(startkapital)          # verfügbares Geld auf dem Konto
        self.gebuehr_satz = gebuehr_prozent / 100   # 0,1 % -> 0.001
        # Positionen: {"AAPL": {"anzahl": 10, "einstand": 1.850,00 (inkl. Gebühren)}}
        self.positionen_daten = {}
        self.transaktionen = []                     # Liste aller Käufe/Verkäufe

    # ---------- interne Hilfsfunktion ----------
    def _pruefe_anzahl(self, anzahl):
        if not isinstance(anzahl, (int, float)) or anzahl <= 0:
            raise ValueError("Die Stückzahl muss eine positive Zahl sein, z. B. 10.")

    def _speichere_transaktion(self, art, symbol, anzahl, kurs_eur, kurs_orig, waehrung, gebuehr, betrag, gewinn=None):
        self.transaktionen.append({
            "Zeitpunkt": datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y %H:%M:%S"),
            "Art": art,
            "Symbol": symbol,
            "Stück": anzahl,
            "Kurs (Original)": f"{kurs_orig:,.2f} {waehrung}",
            "Kurs (€)": round(kurs_eur, 2),
            "Gebühr (€)": round(gebuehr, 2),
            "Betrag (€)": round(betrag, 2),
            "Realisierter Gewinn (€)": None if gewinn is None else round(gewinn, 2),
            "Bargeld danach (€)": round(self.bargeld, 2),
        })

    # ---------- KAUFEN ----------
    def buy(self, symbol, anzahl):
        """Kauft 'anzahl' Aktien von 'symbol' zum aktuellen Kurs. Beispiel: portfolio.buy('AAPL', 10)"""
        symbol = symbol.upper().strip()
        self._pruefe_anzahl(anzahl)
        kurs_eur, kurs_orig, waehrung = hole_aktuellen_kurs(symbol)

        ordervolumen = kurs_eur * anzahl
        gebuehr = ordervolumen * self.gebuehr_satz
        gesamtkosten = ordervolumen + gebuehr

        if gesamtkosten > self.bargeld:
            print(f"❌ Kauf abgelehnt: benötigt {euro(gesamtkosten)}, verfügbar sind nur {euro(self.bargeld)}.")
            return False

        self.bargeld -= gesamtkosten
        position = self.positionen_daten.setdefault(symbol, {"anzahl": 0, "einstand": 0.0})
        position["anzahl"] += anzahl
        position["einstand"] += gesamtkosten       # Gebühren zählen zum Einstandspreis

        self._speichere_transaktion("KAUF", symbol, anzahl, kurs_eur, kurs_orig, waehrung, gebuehr, -gesamtkosten)
        print(f"✅ GEKAUFT: {anzahl} × {symbol} zu {euro(kurs_eur)} "
              f"(Gebühr {euro(gebuehr)}, gesamt {euro(gesamtkosten)}). Bargeld: {euro(self.bargeld)}")
        return True

    # ---------- VERKAUFEN ----------
    def sell(self, symbol, anzahl):
        """Verkauft 'anzahl' Aktien von 'symbol' zum aktuellen Kurs. Beispiel: portfolio.sell('AAPL', 5)"""
        symbol = symbol.upper().strip()
        self._pruefe_anzahl(anzahl)
        position = self.positionen_daten.get(symbol)

        if position is None or position["anzahl"] < anzahl:
            vorhanden = 0 if position is None else position["anzahl"]
            print(f"❌ Verkauf abgelehnt: Sie besitzen nur {vorhanden} Stück {symbol}.")
            return False

        kurs_eur, kurs_orig, waehrung = hole_aktuellen_kurs(symbol)
        verkaufswert = kurs_eur * anzahl
        gebuehr = verkaufswert * self.gebuehr_satz
        erloes = verkaufswert - gebuehr

        # Anteiligen Einstand berechnen, um den Gewinn/Verlust dieses Verkaufs zu ermitteln
        anteiliger_einstand = position["einstand"] * anzahl / position["anzahl"]
        gewinn = erloes - anteiliger_einstand

        self.bargeld += erloes
        position["anzahl"] -= anzahl
        position["einstand"] -= anteiliger_einstand
        if position["anzahl"] == 0:
            del self.positionen_daten[symbol]      # Position komplett verkauft

        self._speichere_transaktion("VERKAUF", symbol, anzahl, kurs_eur, kurs_orig, waehrung, gebuehr, erloes, gewinn)
        print(f"✅ VERKAUFT: {anzahl} × {symbol} zu {euro(kurs_eur)} "
              f"(Gebühr {euro(gebuehr)}, Erlös {euro(erloes)}, Gewinn/Verlust {euro(gewinn)}). "
              f"Bargeld: {euro(self.bargeld)}")
        return True

    # ---------- ÜBERSICHTEN ----------
    def positionen(self):
        """Gibt alle offenen Positionen als Tabelle zurück – mit aktuellem Wert und Gewinn/Verlust."""
        zeilen = []
        for symbol, pos in self.positionen_daten.items():
            kurs_eur, _, _ = hole_aktuellen_kurs(symbol)
            wert = kurs_eur * pos["anzahl"]
            gv = wert - pos["einstand"]
            zeilen.append({
                "Symbol": symbol,
                "Stück": pos["anzahl"],
                "Ø Einstand/Stück (€)": round(pos["einstand"] / pos["anzahl"], 2),
                "Aktueller Kurs (€)": round(kurs_eur, 2),
                "Aktueller Wert (€)": round(wert, 2),
                "Gewinn/Verlust (€)": round(gv, 2),
                "Gewinn/Verlust (%)": round(gv / pos["einstand"] * 100, 2),
            })
        return pd.DataFrame(zeilen)

    def kontostand(self):
        """Druckt eine Zusammenfassung: Bargeld, Depotwert, Gesamtvermögen, Gewinn/Verlust."""
        tabelle = self.positionen()
        depotwert = float(tabelle["Aktueller Wert (€)"].sum()) if not tabelle.empty else 0.0
        gesamt = self.bargeld + depotwert
        gv = gesamt - self.startkapital
        print("=" * 50)
        print("💼 KONTOSTAND")
        print("=" * 50)
        print(f"Bargeld:            {euro(self.bargeld)}")
        print(f"Wert der Aktien:    {euro(depotwert)}")
        print(f"Gesamtvermögen:     {euro(gesamt)}")
        prozent = f"{gv / self.startkapital * 100:+.2f}".replace(".", ",")
        print(f"Gewinn/Verlust:     {euro(gv)} ({prozent} %)")
        print("=" * 50)
        return gesamt

    def historie(self):
        """Gibt alle bisherigen Transaktionen als Tabelle zurück."""
        return pd.DataFrame(self.transaktionen)


# ------------------------------------------------------------
# TEIL C: ANALYSE-LOGIK (Indikatoren und Handelssignal)
# ------------------------------------------------------------

def lade_kursdaten(symbol, zeitraum="2y"):
    """Lädt die Tageskurse (Eröffnung, Hoch, Tief, Schluss, Volumen) der letzten 2 Jahre."""
    daten = yf.Ticker(symbol).history(period=zeitraum, interval="1d")
    if daten.empty:
        raise ValueError(f"Für '{symbol}' wurden keine Kursdaten gefunden. Ist das Kürzel richtig?")
    daten.index = daten.index.tz_localize(None)   # Zeitzone entfernen (für saubere Charts)
    if len(daten) < 200:
        print(f"⚠️ Nur {len(daten)} Handelstage vorhanden – die SMA200 benötigt mindestens 200.")
    return daten


def berechne_indikatoren(daten):
    """
    Fügt den Kursdaten die Indikatoren hinzu:
      SMA50 / SMA200 = Durchschnittskurs der letzten 50 bzw. 200 Tage (Trend)
      RSI            = Stärke der Bewegung von 0–100 (unter 30 überverkauft, über 70 überkauft)
      MACD           = Momentum: Abstand zwischen schnellem und langsamem Durchschnitt
    """
    df = daten.copy()
    schluss = df["Close"]

    if PANDAS_TA_VERFUEGBAR:
        df["SMA50"] = ta.sma(schluss, length=50)
        df["SMA200"] = ta.sma(schluss, length=200)
        df["RSI"] = ta.rsi(schluss, length=14)
        macd = ta.macd(schluss, fast=12, slow=26, signal=9)
        # pandas-ta liefert drei Spalten: MACD-Linie, Histogramm, Signallinie
        df["MACD"] = macd.iloc[:, 0]
        df["MACD_Hist"] = macd.iloc[:, 1]
        df["MACD_Signal"] = macd.iloc[:, 2]
    else:
        # Ersatzberechnung mit denselben Standardformeln
        df["SMA50"] = schluss.rolling(50).mean()
        df["SMA200"] = schluss.rolling(200).mean()
        veraenderung = schluss.diff()
        gewinne = veraenderung.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        verluste = (-veraenderung.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        df["RSI"] = 100 - 100 / (1 + gewinne / verluste)
        df["MACD"] = schluss.ewm(span=12, adjust=False).mean() - schluss.ewm(span=26, adjust=False).mean()
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

    return df


def erzeuge_signal(df):
    """
    Erzeugt nach festen Regeln ein Signal (KAUFEN / HALTEN / VERKAUFEN) aus dem letzten Handelstag.

    Punktesystem (jede Regel gibt +1, -1 oder 0 Punkte):
      1. Kurs über SMA200            -> +1   (sonst -1)   langfristiger Trend
      2. SMA50 über SMA200           -> +1   (sonst -1)   mittelfristiger Trend
      3. MACD über Signallinie       -> +1   (sonst -1)   aktuelles Momentum
      4. RSI unter 30                -> +1   (überverkauft, Erholung möglich)
         RSI über 70                 -> -1   (überkauft, Rücksetzer möglich)
         RSI 30–70                   ->  0   (neutral)

    Entscheidung:
      KAUFEN     bei mindestens +2 Punkten UND RSI unter 70
      VERKAUFEN  bei höchstens  -2 Punkten UND RSI über 30
      HALTEN     in allen anderen Fällen
    """
    letzte = df.dropna(subset=["SMA50", "SMA200", "RSI", "MACD", "MACD_Signal"])
    if letzte.empty:
        return {"signal": "HALTEN", "punkte": 0,
                "begruendung": "Zu wenig Kursdaten, um alle Indikatoren zu berechnen – daher kein klares Signal."}
    z = letzte.iloc[-1]

    kurs_ueber_200 = z["Close"] > z["SMA200"]
    sma50_ueber_200 = z["SMA50"] > z["SMA200"]
    macd_ueber_signal = z["MACD"] > z["MACD_Signal"]
    rsi = z["RSI"]

    punkte = 0
    punkte += 1 if kurs_ueber_200 else -1
    punkte += 1 if sma50_ueber_200 else -1
    punkte += 1 if macd_ueber_signal else -1
    if rsi < 30:
        punkte += 1
        rsi_text = "überverkauft"
    elif rsi > 70:
        punkte -= 1
        rsi_text = "überkauft"
    else:
        rsi_text = "neutral"

    if punkte >= 2 and rsi < 70:
        signal = "KAUFEN"
    elif punkte <= -2 and rsi > 30:
        signal = "VERKAUFEN"
    else:
        signal = "HALTEN"

    begruendung = (
        f"{signal.capitalize()}, weil der Kurs {'über' if kurs_ueber_200 else 'unter'} der SMA200 liegt, "
        f"die SMA50 {'über' if sma50_ueber_200 else 'unter'} der SMA200 verläuft, "
        f"der MACD {'über' if macd_ueber_signal else 'unter'} seiner Signallinie steht "
        f"und der RSI mit {rsi:.0f} {rsi_text} ist (Punktestand {punkte:+d})."
    )

    return {
        "signal": signal,
        "punkte": punkte,
        "begruendung": begruendung,
        "datum": letzte.index[-1].strftime("%d.%m.%Y"),
        "schlusskurs": float(z["Close"]),
        "sma50": float(z["SMA50"]),
        "sma200": float(z["SMA200"]),
        "rsi": float(rsi),
        "macd": float(z["MACD"]),
        "macd_signal": float(z["MACD_Signal"]),
    }


print("✅ Engine geladen: Portfolio-Klasse und Analyse-Funktionen sind bereit. Weiter mit Zelle 3.")
