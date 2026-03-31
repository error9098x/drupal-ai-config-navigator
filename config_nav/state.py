"""
state.py — Reflex application state for the Drupal Config Navigator PoC.

Defines the data models and event handlers that drive the chatbot UI:
  - Message     : a single chat bubble (user or assistant)
  - Candidate   : a ranked config page result from the retrieval layer
  - State       : the root Reflex state with all event handlers

Streaming strategy
------------------
Groq responses are streamed token-by-token.  The `handle_submit` event
handler is an async generator that yields after every token, which causes
Reflex to push incremental WebSocket updates to the React frontend.

The current streaming answer is held in `current_answer` (a plain str var)
rather than in the `messages` list.  Only when streaming is complete is
the final answer appended to `messages`.  This avoids mutating a nested
pydantic model item mid-list, which can cause serialisation issues in some
Reflex versions.
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional

import reflex as rx
from pydantic import BaseModel
from reflex.event import EventSpec

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class Candidate(BaseModel):
    """A single ranked configuration page from the retrieval layer."""

    title: str
    path: str
    module: str
    description: str
    score: float = 0.0


class Message(BaseModel):
    """A chat message — either from the user or the assistant."""

    role: str  # "user" | "assistant"
    content: str


# ---------------------------------------------------------------------------
# Quick-query suggestions shown on the empty-state screen
# ---------------------------------------------------------------------------

QUICK_QUERIES: list[str] = [
    "How do I change the site logo?",
    "Where can I configure email settings?",
    "I need to add a new content type",
    "How do I manage user permissions?",
    "Where is the cache settings page?",
    "How do I put the site in maintenance mode?",
]


# ---------------------------------------------------------------------------
# Application state
# ---------------------------------------------------------------------------


class State(rx.State):
    """
    Root state for the Drupal Config Navigator chat interface.

    Vars
    ----
    messages        : Completed chat messages (user + assistant).
    last_candidates : The ranked config pages returned by the last retrieval.
    current_answer  : Streaming buffer — tokens are appended here in real time.
    question        : The current value of the text input.
    processing      : True while a Groq response is being streamed.
    error_msg       : Non-empty if the last Groq call failed (shown in UI).
    """

    messages: list[Message] = []
    last_candidates: list[Candidate] = []
    current_answer: str = ""
    question: str = ""
    processing: bool = False
    error_msg: str = ""

    # ------------------------------------------------------------------
    # Sync helpers
    # ------------------------------------------------------------------

    def set_question(self, value: str) -> None:
        """Bound to rx.input on_change — keeps `question` in sync."""
        self.question = value

    def clear_chat(self) -> None:
        """Reset the entire conversation."""
        self.messages = []
        self.last_candidates = []
        self.current_answer = ""
        self.error_msg = ""
        self.question = ""
        self.processing = False

    def check_enter(self, key: str) -> Optional[EventSpec]:
        """
        Bound to rx.input on_key_down.
        Returns the handle_submit EventSpec when the user presses Enter.
        """
        if key == "Enter":
            return State.handle_submit  # type: ignore[return-value]
        return None

    def set_quick_query(self, query: str) -> None:
        """
        Bound to the quick-query chip buttons on the empty state screen.
        Pre-fills the input so the user can edit before sending,
        or they can just click Send / press Enter.
        """
        self.question = query

    # ------------------------------------------------------------------
    # Async streaming handler
    # ------------------------------------------------------------------

    async def handle_submit(self) -> AsyncGenerator:  # type: ignore[override]
        """
        Main chat event handler.

        Flow:
          1. Guard: ignore empty queries or re-entrant calls.
          2. Append the user message and yield → frontend shows it immediately.
          3. Run retrieval (sync, fast — no network call).
          4. Store ranked candidates and yield → candidate cards appear.
          5. Stream the Groq response token-by-token, yielding after each chunk.
          6. Append the completed assistant message to `messages` and yield.
        """
        # ---- 1. Guard ------------------------------------------------
        query = self.question.strip()
        if not query or self.processing:
            return

        # ---- 2. User message -----------------------------------------
        self.question = ""
        self.processing = True
        self.error_msg = ""
        self.current_answer = ""
        self.last_candidates = []
        self.messages.append(Message(role="user", content=query))
        yield

        # ---- 3. Retrieval (import lazily to avoid circular imports) ---
        from config_nav.retrieval import retrieve  # noqa: PLC0415

        raw_candidates = retrieve(query, top_k=5)

        # ---- 4. No results -------------------------------------------
        if not raw_candidates:
            self.messages.append(
                Message(
                    role="assistant",
                    content=(
                        "I couldn't find a matching configuration page for that query.\n\n"
                        "**Try rephrasing** — for example, describe what you want to configure "
                        "rather than where it is:\n"
                        "- *'change logo'* instead of *'appearance admin page'*\n"
                        "- *'configure email'* instead of *'mail system'*\n"
                        "- *'add content type'* instead of *'structure settings'*"
                    ),
                )
            )
            self.processing = False
            yield
            return

        # ---- 5. Store candidates ------------------------------------
        self.last_candidates = [
            Candidate(
                title=c["title"],
                path=c["path"],
                module=c.get("module", ""),
                description=c.get("description", ""),
                score=float(c.get("_score", 0.0)),
            )
            for c in raw_candidates
        ]
        yield

        # ---- 6. Stream Groq response ---------------------------------
        from config_nav.groq_client import get_navigation_response  # noqa: PLC0415

        try:
            stream = get_navigation_response(query, raw_candidates)
            for chunk in stream:
                token = chunk.choices[0].delta.content or ""
                if token:
                    self.current_answer += token
                    yield

        except Exception as exc:  # noqa: BLE001
            # Groq failed — build a fallback answer from the top candidate
            top = self.last_candidates[0]
            self.current_answer = (
                f"**Best match:** {top.title} — `{top.path}`\n\n{top.description}"
            )
            self.error_msg = f"Groq API error: {exc}"
            yield

        # ---- 7. Finalise ---------------------------------------------
        # Move the streamed answer from the buffer into the message list
        if self.current_answer.strip():
            self.messages.append(Message(role="assistant", content=self.current_answer))

        self.current_answer = ""
        self.processing = False
        yield
