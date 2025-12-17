# Sanskrit Grammar Analyzer

Sanskrit NLP project that demonstrates a hybrid pipeline:
- text normalization + transliteration
- heuristic sandhi candidate generation
- morphological tagging (lexicon + suffix heuristics)
- candidate ranking with confidence
- explanation layer for top analysis
- web API server + Streamlit frontend app

Note: This is still work in progress project

## Project Structure

```
.
├── app/
│   ├── core/config.py
│   ├── data/
│   │   ├── eval_samples.json
│   │   └── lexicon_sample.json
│   ├── main.py
│   ├── pipeline.py
│   ├── schemas.py
│   └── services/
│       ├── explainer.py
│       ├── morphology.py
│       ├── normalizer.py
│       ├── ranker.py
│       ├── sandhi.py
│       └── transliteration.py
├── ui/streamlit_app.py
├── scripts/evaluate.py
├── tests/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick Start

### 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run API server

```bash
uvicorn app.main:app --reload
```

Open docs at `http://localhost:8000/docs`.

### 3) Run  application UI frontend

```bash
streamlit run ui/streamlit_app.py
```

## What the Project includes:

- **SWE:** API design, modular architecture, tests, Docker
- **NLP/ML:** segmentation candidate generation, token tagging, scoring/ranking, confidence
- **Language engineering:** Sanskrit-specific heuristics and explainability output

## Future Updates (pending)

- Replace transliteration fallback with robust Indic library
- Integrate a true Sanskrit sandhi/morphology engine
- Train ranking model on annotated segmentation data
- Add sutra-level explanation mapping with citations
- Add user feedback loop to impr