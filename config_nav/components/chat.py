"""
components/chat.py — All Reflex UI components for the Drupal Config Navigator.

Components
----------
message_bubble      : A single chat bubble for user or assistant messages.
candidate_card      : A config page result card (title, path, module, description).
candidates_panel    : The ranked list of candidate cards shown below the last answer.
streaming_bubble    : The in-progress answer being streamed from Groq.
empty_state         : Splash screen with quick-query chip buttons.
chat_messages       : The full scrollable message area (empty_state OR message list).
chat_input_bar      : Text input + Send button + Clear button.
"""

from __future__ import annotations

import reflex as rx

from ..state import QUICK_QUERIES, Candidate, Message, State

# ---------------------------------------------------------------------------
# Colour tokens  (dark Tailwind-inspired palette)
# ---------------------------------------------------------------------------

BG_PAGE = "#030712"  # outermost page background
BG_PANEL = "#0A0F1E"  # header / input bar background
BG_CARD = "#0F172A"  # candidate card background
BG_CARD_HOVER = "#1E293B"  # candidate card hover background
BG_ASSISTANT = "#1E293B"  # assistant bubble
BG_USER = "#2563EB"  # user bubble  (blue)
BORDER = "#1E293B"  # subtle border
BORDER_CARD = "#334155"  # card border (slightly lighter)
BORDER_FOCUS = "#3B82F6"  # input focus border
BTN_PRIMARY = "#3B82F6"  # send button background
BTN_PRIMARY_HOVER = "#2563EB"
TEXT_PRIMARY = "#F8FAFC"  # main white text
TEXT_MUTED = "#94A3B8"  # secondary / muted text
TEXT_DIM = "#64748B"  # very dim labels
TEXT_CODE = "#7DD3FC"  # inline code text
TEXT_ERROR = "#F87171"  # error message text
ACCENT_BLUE = "#3B82F6"  # accents / badges


# ---------------------------------------------------------------------------
# message_bubble
# ---------------------------------------------------------------------------


def message_bubble(msg: Message) -> rx.Component:
    """
    Render a single chat message.

    User messages align right with a blue background.
    Assistant messages align left with a dark background.
    Content is rendered as Markdown so **bold**, `code`, and lists work.
    """
    is_user = msg.role == "user"

    return rx.box(
        rx.markdown(
            msg.content,
            component_map={
                "code": lambda value, **props: rx.code(
                    value,
                    color=TEXT_CODE,
                    background="#1E293B",
                    font_size="0.82em",
                    padding="1px 5px",
                    border_radius="4px",
                    **props,
                ),
            },
        ),
        background=rx.cond(is_user, BG_USER, BG_ASSISTANT),
        color=TEXT_PRIMARY,
        padding="10px 15px",
        border_radius=rx.cond(
            is_user,
            "18px 18px 4px 18px",
            "18px 18px 18px 4px",
        ),
        max_width="78%",
        font_size="0.88rem",
        line_height="1.55",
        align_self=rx.cond(is_user, "flex-end", "flex-start"),
        margin_y="3px",
    )


# ---------------------------------------------------------------------------
# candidate_card
# ---------------------------------------------------------------------------


def candidate_card(c: Candidate) -> rx.Component:
    """
    Render a single ranked config-page result.

    Shows: page title · module badge · admin path · short description.
    """
    return rx.box(
        rx.vstack(
            # Row 1: title + module badge
            rx.hstack(
                rx.text(
                    c.title,
                    font_weight="600",
                    color=TEXT_PRIMARY,
                    font_size="0.82rem",
                ),
                rx.spacer(),
                rx.badge(
                    c.module,
                    color_scheme="blue",
                    variant="soft",
                    font_size="0.68rem",
                    padding="1px 7px",
                ),
                width="100%",
                align="center",
            ),
            # Row 2: path in monospace
            rx.text(
                c.path,
                color=TEXT_MUTED,
                font_size="0.72rem",
                font_family="'JetBrains Mono', 'Fira Code', monospace",
            ),
            # Row 3: description
            rx.text(
                c.description,
                color=TEXT_MUTED,
                font_size="0.78rem",
                line_height="1.45",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        background=BG_CARD,
        border=f"1px solid {BORDER_CARD}",
        border_radius="9px",
        padding="10px 14px",
        width="100%",
        cursor="pointer",
        transition="border-color 0.15s ease, background 0.15s ease",
        _hover={
            "border_color": ACCENT_BLUE,
            "background": BG_CARD_HOVER,
        },
    )


# ---------------------------------------------------------------------------
# candidates_panel
# ---------------------------------------------------------------------------


def candidates_panel() -> rx.Component:
    """
    Render the list of ranked candidate cards below the last assistant answer.
    Visible only when last_candidates is non-empty.
    """
    return rx.cond(
        State.last_candidates,
        rx.vstack(
            rx.text(
                "Relevant configuration pages",
                font_size="0.70rem",
                color=TEXT_DIM,
                font_weight="600",
                letter_spacing="0.06em",
                text_transform="uppercase",
                padding_left="2px",
            ),
            rx.foreach(State.last_candidates, candidate_card),
            spacing="2",
            align="stretch",
            width="100%",
            padding="0px 20px 12px 20px",
        ),
        rx.box(),  # render nothing when no candidates
    )


# ---------------------------------------------------------------------------
# streaming_bubble  (in-progress answer)
# ---------------------------------------------------------------------------


def streaming_bubble() -> rx.Component:
    """
    Show the Groq answer as it streams in, token by token.

    - If tokens are arriving  → render current_answer as Markdown.
    - Else if processing      → show a spinner + "Thinking…" label.
    - Otherwise               → render nothing.
    """
    return rx.cond(
        State.current_answer != "",
        # Active streaming — show partial answer
        rx.box(
            rx.markdown(
                State.current_answer,
                component_map={
                    "code": lambda value, **props: rx.code(
                        value,
                        color=TEXT_CODE,
                        background="#1E293B",
                        font_size="0.82em",
                        padding="1px 5px",
                        border_radius="4px",
                        **props,
                    ),
                },
            ),
            background=BG_ASSISTANT,
            color=TEXT_PRIMARY,
            padding="10px 15px",
            border_radius="18px 18px 18px 4px",
            max_width="78%",
            font_size="0.88rem",
            line_height="1.55",
            align_self="flex-start",
            margin_y="3px",
            margin_left="0px",
        ),
        # Waiting for first token
        rx.cond(
            State.processing,
            rx.hstack(
                rx.spinner(size="2", color=TEXT_MUTED),
                rx.text(
                    "Searching configuration index…",
                    color=TEXT_MUTED,
                    font_size="0.82rem",
                    font_style="italic",
                ),
                spacing="2",
                align="center",
                padding_y="6px",
                padding_x="2px",
            ),
            rx.box(),
        ),
    )


# ---------------------------------------------------------------------------
# empty_state
# ---------------------------------------------------------------------------


def _quick_chip(query: str) -> rx.Component:
    """A single quick-query suggestion chip."""
    return rx.button(
        query,
        on_click=State.set_quick_query(query),
        variant="soft",
        color_scheme="gray",
        radius="full",
        size="1",
        cursor="pointer",
        font_size="0.78rem",
        padding="5px 13px",
        _hover={
            "background": BG_CARD_HOVER,
            "color": TEXT_PRIMARY,
        },
    )


def empty_state() -> rx.Component:
    """
    Displayed when the conversation is empty.
    Shows a logo, tagline, and a row of clickable quick-query chips.
    """
    return rx.center(
        rx.vstack(
            # Icon
            rx.icon("compass", size=44, color=BORDER_CARD),
            # Heading
            rx.heading(
                "Drupal Config Navigator",
                size="5",
                color=TEXT_MUTED,
                text_align="center",
            ),
            # Subheading
            rx.text(
                "Ask me anything about Drupal admin configuration",
                color=TEXT_DIM,
                font_size="0.84rem",
                text_align="center",
            ),
            # Quick-query chips
            rx.box(
                rx.flex(
                    *[_quick_chip(q) for q in QUICK_QUERIES],
                    wrap="wrap",
                    gap="2",
                    justify="center",
                ),
                width="100%",
                padding_top="8px",
            ),
            # Hint
            rx.text(
                "Or type your own question below",
                color=TEXT_DIM,
                font_size="0.74rem",
                text_align="center",
                padding_top="4px",
            ),
            spacing="4",
            align="center",
            max_width="520px",
            padding_x="20px",
        ),
        height="100%",
        width="100%",
    )


# ---------------------------------------------------------------------------
# chat_messages  (the main scrollable area)
# ---------------------------------------------------------------------------


def chat_messages() -> rx.Component:
    """
    The scrollable message area.

    Shows `empty_state` when the conversation is empty.
    Otherwise renders the full message history, the live streaming bubble,
    and the candidates panel below.
    """
    return rx.cond(
        State.messages,
        # Conversation in progress
        rx.vstack(
            # Completed messages
            rx.vstack(
                rx.foreach(State.messages, message_bubble),
                # Live streaming answer (empty string = nothing rendered)
                streaming_bubble(),
                align="stretch",
                spacing="0",
                width="100%",
                padding="16px 20px 8px 20px",
            ),
            # Candidate cards (shown below the last answer)
            candidates_panel(),
            spacing="0",
            align="stretch",
            width="100%",
        ),
        # No messages yet
        empty_state(),
    )


# ---------------------------------------------------------------------------
# chat_input_bar
# ---------------------------------------------------------------------------


def chat_input_bar() -> rx.Component:
    """
    The sticky input row at the bottom of the page.

    Contains:
    - A text input (bound to State.question, Enter key submits)
    - A Send button (icon + spinner while processing)
    - A Clear button (only visible when there are messages)
    """
    return rx.hstack(
        # ── Text input ──────────────────────────────────────────────────
        rx.input(
            placeholder="Ask about Drupal config… e.g. 'How do I change the logo?'",
            value=State.question,
            on_change=State.set_question,
            on_key_down=State.check_enter,
            flex="1",
            background=BG_CARD_HOVER,
            border=f"1px solid {BORDER_CARD}",
            color=TEXT_PRIMARY,
            border_radius="10px",
            padding="10px 14px",
            font_size="0.88rem",
            _placeholder={"color": TEXT_DIM},
            _focus={
                "border_color": BORDER_FOCUS,
                "outline": "none",
                "box_shadow": f"0 0 0 2px {BORDER_FOCUS}33",
            },
        ),
        # ── Send button ─────────────────────────────────────────────────
        rx.button(
            rx.cond(
                State.processing,
                rx.spinner(size="2"),
                rx.icon("send", size=17),
            ),
            on_click=State.handle_submit,
            background=BTN_PRIMARY,
            color=TEXT_PRIMARY,
            border_radius="10px",
            padding="10px 18px",
            cursor="pointer",
            _hover={"background": BTN_PRIMARY_HOVER},
            disabled=State.processing,
            min_width="46px",
        ),
        # ── Clear button (only shown when conversation exists) ──────────
        rx.cond(
            State.messages,
            rx.button(
                rx.icon("trash_2", size=16),
                on_click=State.clear_chat,
                background="transparent",
                color=TEXT_DIM,
                border=f"1px solid {BORDER_CARD}",
                border_radius="10px",
                padding="10px 12px",
                cursor="pointer",
                _hover={
                    "color": TEXT_ERROR,
                    "border_color": TEXT_ERROR,
                    "background": "#1a0a0a",
                },
            ),
            rx.box(),  # render nothing when chat is empty
        ),
        width="100%",
        spacing="2",
        align="center",
    )
