import json
from pathlib import Path
from typing import Dict, List

from app.core.config import DATA_DIR


class MorphologyEngine:
    A_STEM_RULES = [
        ("ah", "a", {"vibhakti": "1", "vacana": "sg"}),
        ("am", "a", {"vibhakti": "2", "vacana": "sg"}),
        ("ena", "a", {"vibhakti": "3", "vacana": "sg"}),
        ("asya", "a", {"vibhakti": "6", "vacana": "sg"}),
        ("e", "a", {"vibhakti": "7", "vacana": "sg"}),
        ("ah", "a", {"vibhakti": "1", "vacana": "pl"}),
        ("an", "a", {"vibhakti": "2", "vacana": "pl"}),
    ]

    I_STEM_RULES = [
        ("ih", "i", {"vibhakti": "1", "vacana": "sg"}),
        ("im", "i", {"vibhakti": "2", "vacana": "sg"}),
        ("ina", "i", {"vibhakti": "3", "vacana": "sg"}),
        ("eh", "i", {"vibhakti": "6/5", "vacana": "sg"}),
        ("au", "i", {"vibhakti": "1/2", "vacana": "du"}),
    ]

    def __init__(self, lexicon_path: Path | None = None) -> None:
        path = lexicon_path or (DATA_DIR / "lexicon_sample.json")
        with open(path, "r", encoding="utf-8") as f:
            self.lexicon: Dict[str, List[dict]] = json.load(f)

    def analyze_token(self, token: str) -> List[dict]:
        token = token.lower()
        analyses = []

        if token in self.lexicon:
            analyses.extend(self.lexicon[token])

        analyses.extend(self._parse_a_stem_forms(token))
        analyses.extend(self._parse_i_stem_forms(token))
        # Verb suffix heuristics to keep the MVP robust on unseen words.
        if token.endswith("ti"):
            analyses.append(
                {
                    "lemma": token[:-2] or token,
                    "pos": "VERB",
                    "features": {"lakara": "laT", "purusha": "3", "vacana": "sg"},
                    "confidence": 0.62,
                    "explanation": "Suffix heuristic: -ti often marks present 3rd singular verb forms.",
                }
            )
        if token.endswith("anti"):
            analyses.append(
                {
                    "lemma": token[:-4] or token,
                    "pos": "VERB",
                    "features": {"lakara": "laT", "purusha": "3", "vacana": "pl"},
                    "confidence": 0.66,
                    "explanation": "Suffix heuristic: -anti often marks present 3rd plural verb forms.",
                }
            )

        if not analyses:
            analyses.append(
                {
                    "lemma": token,
                    "pos": "UNK",
                    "features": {"note": "No lexicon hit; fallback guess"},
                    "confidence": 0.2,
                    "explanation": "No confident lexicon or rule match was found.",
                }
            )

        deduped = self._dedupe(analyses)
        deduped.sort(key=lambda x: x["confidence"], reverse=True)
        return deduped[:3]

    def analyze_tokens(self, tokens: List[str]) -> List[List[dict]]:
        return [self.analyze_token(t) for t in tokens]

    def _parse_a_stem_forms(self, token: str) -> List[dict]:
        out: List[dict] = []
        for suffix, replacement, features in self.A_STEM_RULES:
            if not token.endswith(suffix):
                continue
            stem = token[: -len(suffix)] + replacement
            for lex in self.lexicon.get(stem, []):
                if lex["pos"] != "NOUN":
                    continue
                out.append(
                    {
                        "lemma": lex["lemma"],
                        "pos": "NOUN",
                        "features": {**lex.get("features", {}), **features, "stem_class": "a-stem"},
                        "confidence": 0.72,
                        "explanation": f"Ending rule: {token} -> {stem} + {suffix} (a-stem noun heuristic).",
                    }
                )
        return out

    def _parse_i_stem_forms(self, token: str) -> List[dict]:
        out: List[dict] = []
        for suffix, replacement, features in self.I_STEM_RULES:
            if not token.endswith(suffix):
                continue
            stem = token[: -len(suffix)] + replacement
            for lex in self.lexicon.get(stem, []):
                if lex["pos"] != "NOUN":
                    continue
                out.append(
                    {
                        "lemma": lex["lemma"],
                        "pos": "NOUN",
                        "features": {**lex.get("features", {}), **features, "stem_class": "i-stem"},
                        "confidence": 0.7,
                        "explanation": f"Ending rule: {token} -> {stem} + {suffix} (i-stem noun heuristic).",
                    }
                )
        return out

    @staticmethod
    def _dedupe(analyses: List[dict]) -> List[dict]:
        seen = set()
        unique = []
        for analysis in analyses:
            key = (
                analysis.get("lemma"),
                analysis.get("pos"),
                tuple(sorted(analysis.get("features", {}).items())),
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(analysis)
        return unique
