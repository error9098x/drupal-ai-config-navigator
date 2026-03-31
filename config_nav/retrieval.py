"""
retrieval.py — Hybrid configuration page retrieval service.

Pipeline:
  1. Normalise query (lowercase, strip)
  2. Score each record across four weighted signals:
       title match      35%
       description match 25%
       keyword match    25%
       synonym match    15%
  3. Filter by minimum score threshold
  4. Sort descending and return top-k results

No embeddings or external API calls here — this is pure
Python fuzzy/keyword matching using rapidfuzz.
The Groq call happens later, in groq_client.py.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_PATH = Path(__file__).parent / "assets" / "config_data.json"

DEFAULT_TOP_K: int = int(os.environ.get("RETRIEVAL_TOP_K", "5"))
DEFAULT_MIN_SCORE: float = float(os.environ.get("RETRIEVAL_MIN_SCORE", "15"))

# Weights must sum to 1.0
WEIGHT_TITLE = 0.35
WEIGHT_DESC = 0.25
WEIGHT_KEYWORD = 0.25
WEIGHT_SYNONYM = 0.15


# ---------------------------------------------------------------------------
# Data loading (cached so the file is read once per process)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_metadata() -> list[dict[str, Any]]:
    """Load config page records from the JSON asset file."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Config metadata not found at {DATA_PATH}. "
            "Make sure config_data.json exists inside config_nav/assets/."
        )
    with DATA_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def reload_metadata() -> list[dict[str, Any]]:
    """Force a reload of the metadata (clears the lru_cache)."""
    load_metadata.cache_clear()
    return load_metadata()


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------


def _normalise(text: str) -> str:
    """Lowercase and strip whitespace."""
    return text.lower().strip()


def _best_list_score(query: str, items: list[str]) -> float:
    """
    Return the highest partial_ratio score between the query and any item
    in the list.  Returns 0.0 if the list is empty.
    """
    if not items:
        return 0.0
    best = 0.0
    for item in items:
        s = fuzz.partial_ratio(query, _normalise(item))
        if s > best:
            best = s
    return best


def score_record(query: str, record: dict[str, Any]) -> float:
    """
    Compute a weighted relevance score (0–100) for a single config record.

    Signals
    -------
    title      — exact / partial match against the page title
    description— partial match against the human-readable description
    keywords   — best partial match across keyword list
    synonyms   — best partial match across synonym list

    The four signals are blended with the weights defined at the top of
    this module.
    """
    q = _normalise(query)

    # 1. Title (35%) — use token_set_ratio to handle word-order variation
    title_score = fuzz.token_set_ratio(q, _normalise(record.get("title", "")))

    # 2. Description (25%) — partial_ratio; descriptions are longer
    desc_score = fuzz.partial_ratio(q, _normalise(record.get("description", "")))

    # 3. Keywords (25%) — best hit across keyword list
    keyword_score = _best_list_score(q, record.get("keywords", []))

    # 4. Synonyms (15%) — best hit across synonym list
    synonym_score = _best_list_score(q, record.get("synonyms", []))

    return (
        WEIGHT_TITLE * title_score
        + WEIGHT_DESC * desc_score
        + WEIGHT_KEYWORD * keyword_score
        + WEIGHT_SYNONYM * synonym_score
    )


# ---------------------------------------------------------------------------
# Public retrieval function
# ---------------------------------------------------------------------------


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float = DEFAULT_MIN_SCORE,
) -> list[dict[str, Any]]:
    """
    Return up to *top_k* config page records ranked by relevance to *query*.

    Parameters
    ----------
    query:     Natural-language question from the user.
    top_k:     Maximum number of results to return.
    min_score: Records scoring below this threshold are excluded.
               Range: 0–100.  Default: 15 (permissive — catches typos).

    Returns
    -------
    List of record dicts, each augmented with a ``_score`` float key.
    Sorted highest-score first.

    Example
    -------
    >>> results = retrieve("how do I change the logo?")
    >>> results[0]["title"]
    'Appearance / Theme Settings'
    >>> results[0]["path"]
    '/admin/appearance'
    """
    if not query or not query.strip():
        return []

    records = load_metadata()
    scored: list[dict[str, Any]] = []

    for record in records:
        score = score_record(query, record)
        if score >= min_score:
            scored.append({**record, "_score": round(score, 2)})

    # Sort descending by score
    scored.sort(key=lambda r: r["_score"], reverse=True)
    return scored[:top_k]


# ---------------------------------------------------------------------------
# Dev / debug helpers
# ---------------------------------------------------------------------------


def debug_scores(query: str) -> None:
    """
    Print a ranked score table for *query* — useful for prompt tuning.

    Usage (from project root):
        python -c "from config_nav.retrieval import debug_scores; debug_scores('change logo')"
    """
    records = load_metadata()
    scored = []
    for r in records:
        s = score_record(query, r)
        scored.append((s, r["title"], r["path"]))
    scored.sort(reverse=True)

    print(f"\nQuery: '{query}'\n{'─' * 60}")
    print(f"{'Score':>6}  {'Title':<40}  Path")
    print(f"{'─' * 6}  {'─' * 40}  {'─' * 30}")
    for score, title, path in scored[:15]:
        print(f"{score:6.1f}  {title:<40}  {path}")
    print()
