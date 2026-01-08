# src/legend_html.py
from __future__ import annotations

from pathlib import Path
import html


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _dot_items(items: dict[str, str]) -> str:
    # items: {label: color}
    out = []
    for label, color in items.items():
        out.append(
            f"""
            <div class="legend-item">
              <span class="legend-dot" style="background:{_esc(color)};"></span>
              <span>{_esc(label)}</span>
            </div>
            """
        )
    return "".join(out)


def _abbr_full_items(meta: dict[str, dict[str, str]], order: list[str]) -> str:
    out = []
    for k in order:
        m = meta.get(k, {})
        ab = m.get("abbr", k)
        full = m.get("full", k)
        out.append(
            f"""
            <div class="legend-item">
              <span><b>{_esc(ab)}</b> — {_esc(full)}</span>
            </div>
            """
        )
    return "".join(out)


def render_legend_iframe_html(
    *,
    template_path: str,
    css_path: str,
    show_colors: dict[str, str],
    disruption_meta: dict[str, dict[str, str]],
    disruption_order: list[str],
    subset_meta: dict[str, dict[str, str]],
    subset_order: list[str],
) -> str:
    template = Path(template_path).read_text(encoding="utf-8")
    css = Path(css_path).read_text(encoding="utf-8")

    # Build the three sections
    umap_items = _dot_items(show_colors)
    disruption_items = _abbr_full_items(disruption_meta, disruption_order)
    subset_items = _abbr_full_items(subset_meta, subset_order)

    filled = (
        template.replace("{{UMAP_COLOR_ITEMS}}", umap_items)
        .replace("{{DISRUPTION_ITEMS}}", disruption_items)
        .replace("{{SUBSET_ITEMS}}", subset_items)
    )

    # IMPORTANT: components.html runs in an iframe, so we must inject CSS into the iframe.
    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style>{css}</style>
      </head>
      <body style="margin:0; padding:0;">
        {filled}
      </body>
    </html>
    """
