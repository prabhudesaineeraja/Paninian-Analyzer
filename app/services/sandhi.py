from dataclasses import dataclass
from typing import List

from app.core.config import MAX_CANDIDATES, MAX_TOKENS

VOWELS = set("aāiīuūeoṛ")


@dataclass
class SandhiCandidate:
    tokens: List[str]
    rule_hints: List[str]


@dataclass
class SandhiSplitHint:
    left: str
    right: str
    note: str


def _simple_space_tokens(text: str) -> List[str]:
    return [t for t in text.split(" ") if t]


def _generate_heuristic_splits(compact_text: str) -> List[List[str]]:
    """Small heuristic splitter for no-space Sanskrit input."""
    tokens = []
    n = len(compact_text)

    # Greedy split on vowel-consonant boundaries as weak proxy.
    start = 0
    for i in range(1, n):
        prev_ch, ch = compact_text[i - 1], compact_text[i]
        if prev_ch in VOWELS and ch not in VOWELS:
            tokens.append(compact_text[start:i])
            start = i
    tokens.append(compact_text[start:])

    alt = []
    if len(tokens) >= 2:
        merged = tokens[:]
        merged[0:2] = [tokens[0] + tokens[1]]
        alt.append(merged)

    return [tokens] + alt


def _rule_based_binary_splits(token: str) -> List[SandhiSplitHint]:
    hints: List[SandhiSplitHint] = []
    n = len(token)
    for i in range(1, n - 1):
        left_base = token[:i]
        right_base = token[i + 1 :]
        ch = token[i]

        if ch == "ā":
            hints.append(
                SandhiSplitHint(
                    left=left_base + "a",
                    right="a" + right_base,
                    note="savarna-dirgha heuristic: a + a -> a",
                )
            )
        if ch == "e":
            hints.append(
                SandhiSplitHint(
                    left=left_base + "a",
                    right="i" + right_base,
                    note="guna heuristic: a + i -> e",
                )
            )
        if ch == "o":
            hints.append(
                SandhiSplitHint(
                    left=left_base + "a",
                    right="u" + right_base,
                    note="guna heuristic: a + u -> o",
                )
            )

    if "'" in token:
        before, after = token.split("'", 1)
        if before.endswith("o") and after:
            hints.append(
                SandhiSplitHint(
                    left=before[:-1] + "ah",
                    right="a" + after,
                    note="visarga heuristic: ah + a -> o'",
                )
            )
    return hints


def generate_candidates(text_iast: str) -> List[SandhiCandidate]:
    space_tokens = _simple_space_tokens(text_iast)
    candidates: List[SandhiCandidate] = []

    if len(space_tokens) > 1:
        candidates.append(SandhiCandidate(tokens=space_tokens, rule_hints=["Input has explicit pada boundaries"]))
        if len(space_tokens) <= MAX_TOKENS - 1:
            merged = [space_tokens[0] + space_tokens[1]] + space_tokens[2:]
            candidates.append(
                SandhiCandidate(
                    tokens=merged,
                    rule_hints=["Heuristic merge candidate for ambiguous whitespace split"],
                )
            )
    else:
        compact = text_iast.replace(" ", "")
        for split in _generate_heuristic_splits(compact):
            candidates.append(
                SandhiCandidate(
                    tokens=split[:MAX_TOKENS],
                    rule_hints=["Heuristic vowel/consonant segmentation candidate"],
                )
            )
        for hint in _rule_based_binary_splits(compact):
            candidates.append(
                SandhiCandidate(
                    tokens=[hint.left, hint.right],
                    rule_hints=[f"Rule-based split: {hint.note}"],
                )
            )

    unique: List[SandhiCandidate] = []
    seen = set()
    for c in candidates:
        key = tuple(c.tokens)
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)

    return unique[:MAX_CANDIDATES]
