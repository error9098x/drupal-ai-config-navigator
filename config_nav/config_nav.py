"""
config_nav.py — Main Reflex page layout and app initialisation.

This is the entry point that Reflex discovers via rxconfig.py.
It wires together the header, scrollable message area, and input bar
into a full-height dark-themed admin chat interface.

Page structure
--------------
┌─────────────────────────────────────────────────┐
│  header()           ← logo + title + badges      │
├─────────────────────────────────────────────────┤
│                                                   │
│  chat_messages()    ← scrollable, flex: 1         │
│  (empty_state  OR  message list + candidates)     │
│                                                   │
├─────────────────────────────────────────────────┤
│  error_bar()        ← only visible on API error   │
├─────────────────────────────────────────────────┤
│  chat_input_bar()   ← sticky bottom input row     │
└─────────────────────────────────────────────────┘
"""

from __future__ import annotations

import reflex as rx

from .components.chat import chat_input_bar, chat_messages
from .state import State

# ---------------------------------------------------------------------------
# Colour tokens (kept in sync with components/chat.py)
# ---------------------------------------------------------------------------

BG_PAGE = "#030712"
BG_PANEL = "#0A0F1E"
BORDER = "#1E293B"
TEXT_PRIMARY = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
TEXT_DIM = "#64748B"
TEXT_ERROR = "#F87171"
ACCENT_BLUE = "#3B82F6"


# ---------------------------------------------------------------------------
# header
# ---------------------------------------------------------------------------


def header() -> rx.Component:
    """
    Top navigation bar.

    Left  : compass icon + app name + subtitle
    Right : "PoC" badge + "Reflex + Groq" badge
    """
    return rx.hstack(
        # ── Left side ────────────────────────────────────────────────────
        rx.hstack(
            rx.icon("compass", size=22, color=ACCENT_BLUE),
            rx.vstack(
                rx.heading(
                    "Drupal Config Navigator",
                    size="4",
                    color=TEXT_PRIMARY,
                    font_weight="600",
                    line_height="1.2",
                ),
                rx.text(
                    "AI-powered configuration assistant · GSoC 2026 PoC",
                    font_size="0.70rem",
                    color=TEXT_DIM,
                    line_height="1.2",
                ),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        # ── Right side — badges ──────────────────────────────────────────
        rx.hstack(
            rx.badge(
                "PoC",
                color_scheme="blue",
                variant="soft",
                radius="full",
                font_size="0.70rem",
            ),
            rx.badge(
                "Reflex + Groq",
                color_scheme="gray",
                variant="soft",
                radius="full",
                font_size="0.70rem",
            ),
            spacing="2",
            align="center",
        ),
        # ── Row styles ───────────────────────────────────────────────────
        width="100%",
        padding="13px 20px",
        border_bottom=f"1px solid {BORDER}",
        align="center",
        background=BG_PANEL,
        flex_shrink="0",
    )


# ---------------------------------------------------------------------------
# error_bar  (only rendered when State.error_msg is non-empty)
# ---------------------------------------------------------------------------


def error_bar() -> rx.Component:
    """
    A slim red status bar shown when the Groq API call fails.
    Displays the raw error message so the developer can debug quickly.
    """
    return rx.cond(
        State.error_msg != "",
        rx.box(
            rx.hstack(
                rx.icon("triangle_alert", size=13, color=TEXT_ERROR),
                rx.text(
                    State.error_msg,
                    color=TEXT_ERROR,
                    font_size="0.72rem",
                ),
                spacing="2",
                align="center",
            ),
            padding="5px 20px",
            background="#1a0505",
            border_top=f"1px solid #7f1d1d",
            width="100%",
            flex_shrink="0",
        ),
        rx.box(),  # render nothing when no error
    )


# ---------------------------------------------------------------------------
# index  (main page)
# ---------------------------------------------------------------------------


REMOVE_REFLEX_BADGE_SCRIPT = """
// Remove "Built with Reflex" badge that gets auto-injected on deploy
(function() {
    function removeReflexBadge() {
        const links = document.querySelectorAll('a[href="https://reflex.dev"]');
        links.forEach(link => {
            const text = link.textContent || '';
            if (text.includes('Built with Reflex')) {
                link.remove();
            }
        });
    }
    
    // Initial removal
    removeReflexBadge();
    
    // Watch for dynamically injected elements
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    if (node.tagName === 'A' && node.href === 'https://reflex.dev' && 
                        node.textContent && node.textContent.includes('Built with Reflex')) {
                        node.remove();
                    } else if (node.querySelectorAll) {
                        const badges = node.querySelectorAll('a[href="https://reflex.dev"]');
                        badges.forEach(badge => {
                            if (badge.textContent && badge.textContent.includes('Built with Reflex')) {
                                badge.remove();
                            }
                        });
                    }
                }
            });
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
})();
"""


def index() -> rx.Component:
    """
    Full-height single-page layout.

    The middle section (chat_messages) is given flex="1" and overflow_y="auto"
    so it scrolls independently while the header and input bar stay fixed.
    The outer box constrains the max width to 900 px and centres it.
    """
    return rx.box(
        rx.script(REMOVE_REFLEX_BADGE_SCRIPT),
        rx.vstack(
            header(),
            rx.box(
                chat_messages(),
                flex="1",
                overflow_y="auto",
                width="100%",
                padding_bottom="8px",
            ),
            error_bar(),
            rx.box(
                chat_input_bar(),
                padding="12px 20px",
                border_top=f"1px solid {BORDER}",
                width="100%",
                background=BG_PANEL,
                flex_shrink="0",
            ),
            spacing="0",
            align="stretch",
            height="100vh",
            width="100%",
        ),
        background=BG_PAGE,
        min_height="100vh",
        width="100%",
    )


# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
    # Global style overrides applied to the <html> / <body> elements
    style={
        "font_family": (
            "'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
        ),
        "background": BG_PAGE,
    },
)

app.add_page(
    index,
    route="/",
    title="Drupal Config Navigator — GSoC 2026 PoC",
    description=(
        "AI-powered Drupal admin configuration assistant. "
        "Built with Reflex + Groq for the GSoC 2026 proposal."
    ),
)
