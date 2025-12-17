from typing import List


def build_explanation(tokens: List[str], rule_hints: List[str], token_analyses: List[List[dict]], raw_score: float) -> List[str]:
    notes = []
    notes.append(f"Candidate scored {raw_score:.3f} from lexical coverage and morphology confidence.")

    known_count = sum(1 for analyses in token_analyses if analyses and analyses[0]["pos"] != "UNK")
    notes.append(f"{known_count}/{len(tokens)} tokens matched lexicon or suffix grammar heuristics.")

    if rule_hints:
        notes.extend([f"Sandhi hint: {h}" for h in rule_hints])
    else:
        notes.append("Direct analysis: no explicit sandhi split rule was applied.")

    for token, analyses in zip(tokens, token_analyses):
        if not analyses:
            continue
        best = analyses[0]
        token_note = best.get("explanation")
        if token_note:
            notes.append(f"Token '{token}': {token_note}")

    notes.append("Reference: Paninian-style explainability layer (expand to exact sutra mapping in v2).")
    return notes
