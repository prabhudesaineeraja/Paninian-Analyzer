from typing import Tuple

DEVANAGARI_RANGE = ("\u0900", "\u097F")


def _is_devanagari(text: str) -> bool:
    return any(DEVANAGARI_RANGE[0] <= ch <= DEVANAGARI_RANGE[1] for ch in text)


def to_iast_approx(text: str) -> Tuple[str, str]:
    """Return (normalized_text, iast_like_text).

    This is a lightweight fallback transliteration. For production, replace with
    Indic NLP / indic-transliteration package.
    """
    normalized = text.replace("।", " ").strip()
    if not _is_devanagari(normalized):
        return normalized, normalized.lower()

    # Minimal map for common demo words. Unknown chars are dropped conservatively.
    char_map = {
        "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
        "ऋ": "ṛ", "ए": "e", "ओ": "o", "क": "k", "ख": "kh", "ग": "g",
        "घ": "gh", "च": "c", "ज": "j", "ट": "ṭ", "ड": "ḍ", "त": "t",
        "द": "d", "न": "n", "प": "p", "ब": "b", "म": "m", "य": "y",
        "र": "r", "ल": "l", "व": "v", "श": "ś", "ष": "ṣ", "स": "s",
        "ह": "h", "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū",
        "े": "e", "ो": "o", "ं": "ṃ", "ः": "ḥ", "्": "", " ": " ",
    }

    out = []
    for ch in normalized:
        out.append(char_map.get(ch, ""))
    iast = "".join(out)
    iast = " ".join(iast.split())
    return normalized, iast.lower()
