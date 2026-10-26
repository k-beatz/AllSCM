# Aktienanalyse

Eine lokal laufende Anwendung, die eine Aktie per Kürzel analysiert und die Empfehlung
**Kaufen / Halten / Verkaufen** mit Begründung anzeigt. Die Oberfläche öffnet sich im Browser.

> ⚠️ **Keine Anlageberatung.** Die Software ist ein Lern- und Experimentierwerkzeug.
> Sie führt keine echten Orders aus.

**Aktueller Stand: Phase 1 (Charts).** Die Empfehlung beruht vorläufig nur auf vier technischen
Indikatoren (gleitende Durchschnitte, RSI, MACD, Bollinger-Bänder). Die News-Analyse mit KI kommt in Phase 2.

## Installation unter Windows (einmalig)

1. **Python installieren:** Unter <https://www.python.org/downloads/> Python 3.11 oder neuer
   herunterladen. Beim Installieren unbedingt das Häkchen **„Add python.exe to PATH“** setzen.
2. **Projekt herunterladen** und den Ordner `aktienanalyse` an einen beliebigen Ort legen.

## Starten

**Am einfachsten:** Im Ordner `aktienanalyse` doppelt auf **`start.bat`** klicken.
Beim ersten Start legt die Datei eine virtuelle Umgebung an und installiert alle Bibliotheken
(dauert ein paar Minuten). Danach öffnet sich der Browser mit der App.

**Alternativ von Hand** in der Eingabeaufforderung (im Ordner `aktienanalyse`):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Ab dem zweiten Mal reichen `.venv\Scripts\activate` und `streamlit run app.py`.
Beenden: Im schwarzen Fenster `Strg + C` drücken oder das Fenster schließen.

## Bedienung

1. Aktienkürzel eingeben, z. B. `AAPL` (Apple), `MSFT` (Microsoft) oder `SAP.DE` (deutsche Börse: Endung `.DE`).
2. Zeitraum wählen und auf **Analysieren** klicken.
3. Oben steht die Empfehlung, darunter der Chart, dann die Tabelle mit allen Teilsignalen.

## So entsteht die Empfehlung

| Indikator | Positiv (+1) | Negativ (−1) | Gewicht |
|---|---|---|---|
| Trend (SMA 50/200) | Kurs über SMA200 und SMA50 über SMA200 | Kurs unter SMA200 und SMA50 unter SMA200 | 40 % |
| MACD (12/26/9) | MACD über Signallinie | MACD unter Signallinie | 25 % |
| RSI (14) | unter 30 (überverkauft) | über 70 (überkauft) | 20 % |
| Bollinger (20, 2σ) | Kurs am unteren Band | Kurs am oberen Band | 15 % |

Alles andere zählt als neutral (0). Der **Chart-Score** ist der gewichtete Mittelwert (−1 bis +1).
Über **+0,3** heißt es *Kaufen*, unter **−0,3** *Verkaufen*, sonst *Halten*.
Alle Werte stehen in `config.py` und lassen sich dort ändern.

Für die Indikatoren werden immer mindestens 2 Jahre Kurse geladen (der SMA200 braucht 200 Handelstage),
auch wenn im Chart ein kürzerer Zeitraum angezeigt wird.

Die Indikatoren werden direkt mit pandas berechnet statt mit pandas-ta: Die aktuelle pandas-ta-Version
braucht Python 3.12 oder neuer, die ältere funktioniert nicht mit aktuellem numpy.

## Tests

```bat
.venv\Scripts\activate
pytest
```

## Ordnerstruktur

```
aktienanalyse/
├── app.py              # Streamlit-Oberfläche
├── config.py           # Gewichte, Schwellenwerte, Indikator-Einstellungen
├── start.bat           # Start per Doppelklick (Windows)
├── data/prices.py      # Kursdaten holen (Schnittstelle + yfinance)
├── analysis/
│   ├── technical.py    # Indikatoren -> Chart-Score
│   └── decision.py     # Score -> Empfehlung + Begründung
└── tests/              # pytest-Tests
```

Später kommen dazu: `data/news.py`, `analysis/sentiment.py`, `storage/cache.py` (Phase 2),
`backtest/` (Phase 3) und `broker/` (Phase 4).
