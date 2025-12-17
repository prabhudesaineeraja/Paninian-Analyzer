import os
import requests
import streamlit as st

API_URL = os.getenv("SANSKRIT_API_URL", "http://localhost:8000")
SAMPLE_INPUTS = [
    "ramah vanam gacchati",
    "krishnah pustakam pathati",
    "sita phalam pashyati",
    "narah phalam khadati",
    "devo'sti",
    "sita ca krishnah ca",
    "ramam krishnah pashyati"
]


def infer_karaka(features: dict, pos: str) -> tuple[str, str]:
    if pos != "NOUN":
        return "-", "Non-nominal token"

    hint = features.get("karaka_hint")
    if hint:
        return hint, "Lexicon-provided karaka hint"

    vib = str(features.get("vibhakti", ""))
    if vib.startswith("1"):
        return "kartā", "Heuristic: nominative tends to subject"
    if vib.startswith("2"):
        return "karma", "Heuristic: accusative tends to object"
    if "3" in vib:
        return "karaṇa", "Heuristic: instrumental tends to instrument"
    if "7" in vib:
        return "adhikaraṇa", "Heuristic: locative tends to location"
    return "unknown", "No reliable karaka signal"

st.set_page_config(page_title="Explainable Sanskrit Analyzer", page_icon="📚", layout="wide")
st.title("Explainable Sanskrit Analyzer")
st.caption("1-week MVP: sandhi candidates + morphology + ranked analysis")

st.markdown("**Try a demo sentence**")
selected_example = st.selectbox("Examples", SAMPLE_INPUTS, index=0)
if st.button("Load Example"):
    st.session_state["input_text"] = selected_example

if "input_text" not in st.session_state:
    st.session_state["input_text"] = SAMPLE_INPUTS[0]

text = st.text_area("Enter Sanskrit text (Devanagari or IAST)", key="input_text", height=100)
top_k = st.slider("Top-k analyses", min_value=1, max_value=5, value=3)

if st.button("Analyze"):
    if not text.strip():
        st.warning("Please enter text.")
    else:
        try:
            with st.spinner("Analyzing..."):
                resp = requests.post(f"{API_URL}/analyze", json={"text": text, "top_k": top_k}, timeout=20)
        except requests.exceptions.RequestException as exc:
            st.error(f"Could not connect to backend at {API_URL}. Details: {exc}")
            st.stop()

        if resp.status_code != 200:
            st.error(f"API error: {resp.status_code} - {resp.text}")
        else:
            data = resp.json()

            st.subheader("Input")
            st.write(f"Normalized: `{data['normalized_text']}`")
            st.write(f"IAST-like: `{data['transliterated_text']}`")
            st.write(f"Pipeline version: `{data['pipeline_version']}`")

            top = data["top_analysis"]
            st.subheader("Top Analysis")
            st.write(f"Rank: {top['rank']} | Confidence: {top['confidence']}")
            st.write("Tokens:", " | ".join(top["tokens"]))

            st.markdown("**Token-level Morphology**")
            rows = []
            for t in top["token_analyses"]:
                best = t["analyses"][0]
                rows.append(
                    {
                        "token": t["token"],
                        "lemma": best["lemma"],
                        "pos": best["pos"],
                        "features": best["features"],
                        "conf": best["confidence"],
                        "analysis_note": best.get("explanation"),
                    }
                )
            st.dataframe(rows, use_container_width=True)

            st.markdown("**Karaka View (Paninian-style heuristic)**")
            karaka_rows = []
            for t in top["token_analyses"]:
                best = t["analyses"][0]
                role, rationale = infer_karaka(best.get("features", {}), best.get("pos", ""))
                karaka_rows.append(
                    {
                        "token": t["token"],
                        "lemma": best.get("lemma"),
                        "pos": best.get("pos"),
                        "predicted_karaka": role,
                        "rationale": rationale,
                    }
                )
            st.dataframe(karaka_rows, use_container_width=True)

            st.markdown("**Why this analysis?**")
            for note in top["explanation"]:
                st.write(f"- {note}")

            st.subheader("Alternative Candidates")
            if not data["alternatives"]:
                st.info("No alternatives generated for this input.")
            else:
                for alt in data["alternatives"]:
                    st.markdown(f"**Rank {alt['rank']}** | confidence `{alt['confidence']}`")
                    st.write("Tokens:", " | ".join(alt["tokens"]))
