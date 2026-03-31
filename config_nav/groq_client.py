"""
groq_client.py — Groq API integration for the Drupal Config Navigator PoC.

Responsibilities:
- Accept a user query + ranked config candidates from the retrieval layer
- Build a structured prompt that frames the LLM as a Drupal navigation assistant
- Stream the response back token-by-token using the Groq Python SDK
- Provide a safe fallback if the API call fails
"""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
# This is the core instruction set for the LLM. It tells the model exactly
# what role it plays, what format to respond in, and what NOT to do.
# Keeping it tight reduces hallucination and keeps responses actionable.
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a helpful Drupal admin configuration assistant embedded in the site's admin interface.

Your role is to help site builders and administrators find the right Drupal configuration page and understand how to use it.

You will receive:
1. The user's question
2. A ranked list of relevant Drupal configuration pages with their paths and descriptions

Guidelines for your response:
- Start by identifying the best matching page with its path
- Provide a clear, helpful explanation of what the page does and how to use it
- Mention other relevant pages if they might be helpful
- Use a conversational, friendly tone while being concise
- Include practical tips when relevant
- Always include exact admin paths in backticks
- Never invent paths that weren't in the candidate list
- Use plain language and avoid heavy jargon

Your response should be helpful and actionable. Aim for 150-250 words to provide good context without overwhelming the user.

Example structure (feel free to adapt):
"The best place to [answer their question] is the **[Page Title]** page at `[/admin/path]`. 

This page lets you [explain what it does]. [Optional: Here's how to use it / what to look for.]

If you also need to [related task], check out `[/admin/other-path]` for [brief explanation]."
"""

# ---------------------------------------------------------------------------
# Model + inference defaults
# ---------------------------------------------------------------------------

_DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
_DEFAULT_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1500"))
_DEFAULT_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.5"))
_DEFAULT_REASONING_EFFORT = os.getenv("GROQ_REASONING_EFFORT", "medium")


def _build_user_message(query: str, candidates: list[dict]) -> str:
    """
    Format the user message that will be sent to the model.

    The message includes the raw user query plus a formatted list of the
    top-ranked candidate config pages from the retrieval layer.
    """
    if not candidates:
        return f'User question: "{query}"\n\nNo matching configuration pages were found in the index.'

    lines = []
    for i, c in enumerate(candidates[:5], start=1):
        score = c.get("_score", 0.0)
        lines.append(
            f"{i}. **{c['title']}** (`{c['path']}`)\n"
            f"   Module: {c.get('module', 'unknown')} | Match score: {score:.1f}\n"
            f"   {c.get('description', '')}"
        )

    candidates_block = "\n\n".join(lines)

    return (
        f'User question: "{query}"\n\n'
        f"Ranked configuration pages found:\n\n"
        f"{candidates_block}\n\n"
        f"Which page best answers the user's question?"
    )


def get_navigation_response(query: str, candidates: list[dict]):
    """
    Stream a navigation explanation from Groq given a user query and candidates.

    Args:
        query:      The raw natural-language question from the user.
        candidates: Ranked list of config page dicts from retrieval.retrieve().
                    Each dict has: title, path, module, description, _score, keywords, synonyms.

    Returns:
        A Groq streaming completion iterator.
        Callers should iterate over it:

            stream = get_navigation_response(query, candidates)
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                print(delta, end="", flush=True)

    Raises:
        Exception: Re-raises Groq API errors so the caller can handle them
                   (e.g. show a fallback in the UI).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. "
            "Copy .env.example to .env and add your key from https://console.groq.com/keys"
        )

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model=_DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(query, candidates)},
        ],
        temperature=_DEFAULT_TEMPERATURE,
        max_completion_tokens=_DEFAULT_MAX_TOKENS,
        top_p=1,
        reasoning_effort=_DEFAULT_REASONING_EFFORT,
        stream=True,
        stop=None,
    )

    return completion


def get_navigation_response_safe(query: str, candidates: list[dict]) -> str:
    """
    Non-streaming fallback that returns the full response as a string.

    Use this when streaming is unavailable or when you want to capture the
    complete answer before rendering (e.g. for evaluation / logging).

    Returns a plain string, never raises — on error returns a formatted
    fallback built directly from the top candidate.
    """
    try:
        stream = get_navigation_response(query, candidates)
        full_text = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_text += delta
        return full_text.strip()

    except Exception as exc:  # noqa: BLE001
        if candidates:
            top = candidates[0]
            return (
                f"**Best match:** {top['title']} — `{top['path']}`\n\n"
                f"{top.get('description', '')}\n\n"
                f"*(Groq API unavailable: {exc})*"
            )
        return (
            f"No matching configuration page found for: *{query}*\n\n"
            f"*(Groq API unavailable: {exc})*"
        )
