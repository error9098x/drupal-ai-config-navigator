import reflex as rx

config = rx.Config(
    app_name="config_nav",
    db_url="sqlite:///config_nav.db",
    env=rx.Env.DEV,
    # ── Plugins ──────────────────────────────────────────────────────────────
    # Explicitly declare SitemapPlugin so Reflex does not emit the
    # "plugin is enabled by default but not explicitly added" warning.
    # Remove it (or move to disable_plugins) if you don't want a sitemap.
    plugins=[rx.plugins.SitemapPlugin()],
    # ── State setters ────────────────────────────────────────────────────────
    # Reflex 0.8.9+ deprecated the implicit auto-setter default (True).
    # Set it explicitly to keep current behaviour and silence the warning.
    # We define our own set_* methods in state.py, so False would also work,
    # but True is the safest default for a first run.
    state_auto_setters=True,
)
