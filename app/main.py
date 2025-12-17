from fastapi import FastAPI

from app.pipeline import SanskritAnalyzerPipeline
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.normalizer import normalize_text
from app.services.transliteration import to_iast_approx

app = FastAPI(title="Explainable Sanskrit Analyzer", version="0.1.0")
pipeline = SanskritAnalyzerPipeline()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sanskrit-analyzer"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    normalized = normalize_text(payload.text)
    normalized_for_iast, iast_text = to_iast_approx(normalized)
    candidates = pipeline.run(iast_text, top_k=payload.top_k)

    top = candidates[0]
    alternatives = candidates[1:] if len(candidates) > 1 else []

    return AnalyzeResponse(
        input_text=payload.text,
        normalized_text=normalized_for_iast,
        transliterated_text=iast_text,
        top_analysis=top,
        alternatives=alternatives,
        pipeline_version="heuristic-ranker-v0.2",
        notes=[
            "MVP uses heuristics + lexical scoring. Swap with trained model in v2.",
            "Transliteration is approximate fallback for demo words.",
        ],
    )
