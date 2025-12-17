from app.pipeline import SanskritAnalyzerPipeline
from app.services.normalizer import normalize_text
from app.services.transliteration import to_iast_approx


def test_pipeline_returns_ranked_candidates() -> None:
    p = SanskritAnalyzerPipeline()
    text = normalize_text("rama gacchati vanam")
    _, iast = to_iast_approx(text)
    cands = p.run(iast, top_k=3)

    assert len(cands) >= 1
    assert cands[0].rank == 1
    assert cands[0].confidence >= 0
    assert len(cands[0].token_analyses) == len(cands[0].tokens)
