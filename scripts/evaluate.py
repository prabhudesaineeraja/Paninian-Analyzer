import json
from pathlib import Path

from app.pipeline import SanskritAnalyzerPipeline
from app.services.normalizer import normalize_text
from app.services.transliteration import to_iast_approx


def main() -> None:
    data_path = Path("app/data/eval_samples.json")
    with open(data_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    pipeline = SanskritAnalyzerPipeline()
    correct = 0

    for sample in samples:
        normalized = normalize_text(sample["input"])
        _, iast = to_iast_approx(normalized)
        out = pipeline.run(iast, top_k=1)
        pred = out[0].tokens
        expected = sample["expected_top_tokens"]
        hit = pred == expected
        correct += int(hit)
        print(f"input={sample['input']}\npred={pred}\nexp={expected}\nmatch={hit}\n")

    acc = correct / len(samples) if samples else 0.0
    print(f"Top-1 exact token sequence accuracy: {acc:.2%}")


if __name__ == "__main__":
    main()
