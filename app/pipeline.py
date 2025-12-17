from app.schemas import CandidateAnalysis, MorphTag, TokenAnalysis
from app.services.explainer import build_explanation
from app.services.morphology import MorphologyEngine
from app.services.ranker import rank_candidates
from app.services.sandhi import generate_candidates


class SanskritAnalyzerPipeline:
    def __init__(self) -> None:
        self.morph_engine = MorphologyEngine()

    def run(self, text_iast: str, top_k: int = 3) -> list[CandidateAnalysis]:
        sandhi_candidates = generate_candidates(text_iast)
        enriched = []

        for candidate in sandhi_candidates:
            token_analyses = self.morph_engine.analyze_tokens(candidate.tokens)
            enriched.append(
                {
                    "tokens": candidate.tokens,
                    "token_analyses": token_analyses,
                    "rule_hints": candidate.rule_hints,
                }
            )

        ranked = rank_candidates(enriched)

        response_candidates: list[CandidateAnalysis] = []
        for c in ranked[:top_k]:
            token_items = []
            for token, analyses in zip(c["tokens"], c["token_analyses"]):
                morph_items = [
                    MorphTag(
                        lemma=a["lemma"],
                        pos=a["pos"],
                        features=a["features"],
                        confidence=a["confidence"],
                        explanation=a.get("explanation"),
                        gloss=a.get("gloss"),
                    )
                    for a in analyses
                ]
                token_items.append(TokenAnalysis(token=token, analyses=morph_items))

            explanation = build_explanation(c["tokens"], c["rule_hints"], c["token_analyses"], c["raw_score"])
            response_candidates.append(
                CandidateAnalysis(
                    rank=c["rank"],
                    confidence=c["confidence"],
                    tokens=c["tokens"],
                    token_analyses=token_items,
                    explanation=explanation,
                )
            )

        return response_candidates
