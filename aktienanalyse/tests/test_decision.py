"""Einfache Tests für die Entscheidungsregeln (Start: pytest)."""

from analysis import decision
from analysis.technical import Signal, TechnicalResult


def make_result(score: float) -> TechnicalResult:
    """Erzeugt ein Chart-Ergebnis mit vorgegebenem Score."""
    signals = [Signal("trend", "Trend (SMA50/200)", "", 1.0 if score > 0 else -1.0, 0.4, "")]
    return TechnicalResult(score=score, signals=signals)


def test_recommend_kaufen():
    assert decision.recommend(0.5) == decision.BUY


def test_recommend_verkaufen():
    assert decision.recommend(-0.5) == decision.SELL


def test_recommend_halten_zwischen_den_schwellen():
    assert decision.recommend(0.0) == decision.HOLD
    assert decision.recommend(0.3) == decision.HOLD    # genau auf der Schwelle -> Halten
    assert decision.recommend(-0.3) == decision.HOLD


def test_recommend_eigene_schwellen():
    assert decision.recommend(0.2, buy_threshold=0.1, sell_threshold=-0.1) == decision.BUY


def test_decide_liefert_alles_zurueck():
    result = decision.decide(make_result(0.65))
    assert result.recommendation == decision.BUY
    assert result.total_score == 0.65
    assert len(result.signals) == 1
    assert "Trend" in result.reason
