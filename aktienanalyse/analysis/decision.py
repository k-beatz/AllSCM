"""Entscheidung: aus den Scores wird eine Empfehlung mit Begründung.

Feste, nachvollziehbare Regeln – keine KI.
Phase 1: Die Empfehlung beruht vorläufig nur auf dem Chart-Score.
In Phase 2 kommt hier der News-Score dazu.
"""

from dataclasses import dataclass

import config
from analysis.technical import Signal, TechnicalResult

BUY = "Kaufen"
HOLD = "Halten"
SELL = "Verkaufen"


@dataclass
class Decision:
    """Empfehlung samt Gesamtscore, allen Teilsignalen und Begründung."""

    recommendation: str
    total_score: float
    chart_score: float
    signals: list[Signal]
    reason: str


def recommend(score: float, buy_threshold: float = config.BUY_THRESHOLD,
              sell_threshold: float = config.SELL_THRESHOLD) -> str:
    """Übersetzt einen Score in Kaufen / Halten / Verkaufen."""
    if score > buy_threshold:
        return BUY
    if score < sell_threshold:
        return SELL
    return HOLD


def decide(technical: TechnicalResult, buy_threshold: float = config.BUY_THRESHOLD,
           sell_threshold: float = config.SELL_THRESHOLD) -> Decision:
    """Vorläufige Empfehlung nur aus der Chart-Analyse."""
    score = technical.score
    recommendation = recommend(score, buy_threshold, sell_threshold)
    return Decision(
        recommendation=recommendation,
        total_score=score,
        chart_score=score,
        signals=technical.signals,
        reason=_reason(recommendation, score, technical.signals, buy_threshold, sell_threshold),
    )


def _reason(recommendation: str, score: float, signals: list[Signal],
            buy_threshold: float, sell_threshold: float) -> str:
    """Baut einen kurzen Begründungssatz aus den Teilsignalen."""
    positive = [s.name.split(" (")[0] for s in signals if s.signal > 0]
    negative = [s.name.split(" (")[0] for s in signals if s.signal < 0]
    parts = []
    if positive:
        parts.append("positiv: " + ", ".join(positive))
    if negative:
        parts.append("negativ: " + ", ".join(negative))
    detail = "; ".join(parts) if parts else "alle Teilsignale neutral"

    if recommendation == BUY:
        rule = f"liegt über der Kaufschwelle von {buy_threshold:+.2f}"
    elif recommendation == SELL:
        rule = f"liegt unter der Verkaufsschwelle von {sell_threshold:+.2f}"
    else:
        rule = f"liegt zwischen {sell_threshold:+.2f} und {buy_threshold:+.2f}"
    return f"Der Chart-Score von {score:+.2f} {rule} ({detail})."
