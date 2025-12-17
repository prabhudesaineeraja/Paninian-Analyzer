from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, description="Sanskrit input in Devanagari or IAST")
    top_k: int = Field(default=3, ge=1, le=10)


class MorphTag(BaseModel):
    lemma: str
    pos: str
    features: dict
    confidence: float
    explanation: str | None = None
    gloss: str | None = None


class TokenAnalysis(BaseModel):
    token: str
    analyses: List[MorphTag]


class CandidateAnalysis(BaseModel):
    rank: int
    confidence: float
    tokens: List[str]
    token_analyses: List[TokenAnalysis]
    explanation: List[str]


class AnalyzeResponse(BaseModel):
    input_text: str
    normalized_text: str
    transliterated_text: str
    top_analysis: CandidateAnalysis
    alternatives: List[CandidateAnalysis]
    pipeline_version: str
    notes: Optional[List[str]] = None
