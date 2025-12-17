from math import exp
from typing import List


def _softmax(scores: List[float]) -> List[float]:
    if not scores:
        return []
    m = max(scores)
    e = [exp(s - m) for s in scores]
    z = sum(e)
    return [x / z for x in e]


def score_candidate(tokens: List[str], analyses: List[List[dict]]) -> float:
    total = len(tokens) if tokens else 1
    known = sum(1 for a in analyses if a and a[0]["pos"] != "UNK") / total
    avg_conf = sum(a[0]["confidence"] for a in analyses if a) / total

    # Encourage medium token counts in this MVP (avoid over-merge or over-split).
    length_penalty = max(0.0, 1.0 - abs(len(tokens) - 3) * 0.2)

    return 0.5 * known + 0.35 * avg_conf + 0.15 * length_penalty


def rank_candidates(candidates: List[dict]) -> List[dict]:
    raw_scores = []
    for c in candidates:
        base = score_candidate(c["tokens"], c["token_analyses"])
        sandhi_bonus = 0.04 if c.get("rule_hints") else 0.0
        complexity_penalty = max(0, len(c["tokens"]) - 4) * 0.02
        raw_scores.append(base + sandhi_bonus - complexity_penalty)
    probs = _softmax(raw_scores)

    enriched = []
    for i, c in enumerate(candidates):
        c_copy = c.copy()
        c_copy["confidence"] = round(probs[i], 4)
        c_copy["raw_score"] = round(raw_scores[i], 4)
        enriched.append(c_copy)

    enriched.sort(key=lambda x: x["confidence"], reverse=True)
    for idx, item in enumerate(enriched, start=1):
        item["rank"] = idx
    return enriched
