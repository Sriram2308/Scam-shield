"""Explanation layer. Baseline: look up a vetted advisory by scam type and language.
Upgrade path: replace `advise` with a LangChain + ChromaDB retriever over RBI/NPCI/I4C advisories."""
import json
from functools import lru_cache
from pathlib import Path

ADVISORY_PATH = Path(__file__).resolve().parent.parent / "data" / "advisories.json"
LANGS = ("en", "ta", "hi")


@lru_cache(maxsize=1)
def _kb() -> dict:
    with open(ADVISORY_PATH, encoding="utf-8") as f:
        return json.load(f)


def advise(result: dict, lang: str = "en") -> dict:
    lang = lang if lang in LANGS else "en"
    kb = _kb()
    if result["level"] == "likely_safe":
        return {"explanation": kb["safe"][lang], "steps": [], "sources": kb["sources"]}
    entry = kb["types"].get(result["scam_type"] or "generic", kb["types"]["generic"])
    return {"explanation": entry[lang], "steps": kb["steps"][lang], "sources": kb["sources"]}
