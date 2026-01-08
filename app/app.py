# app.py

import os
import streamlit as st
import pandas as pd
from pathlib import Path

from src.data_io import read_uploaded_file, read_default_path
from src.silhouette_grid import render_silhouette_grid
from src.umap_plot import make_umap_plot
from src.label_meta import (
    DISRUPTION_META, DISRUPTION_ORDER, DISRUPTION_LEGEND_META, SUBSET_META, SUBSET_ORDER, SUBSET_LEGEND_ORDER, SUBSET_LEGEND_META, full, SHOW_COLORS)
import streamlit.components.v1 as components
from src.legend import render_legend_iframe_html


def load_css(path: str):
    st.markdown(f"<style>{Path(path).read_text()}</style>",
                unsafe_allow_html=True)


load_css("src/styles/app.css")

# -----------------------------
# Page config + tight layout
# -----------------------------
st.set_page_config(layout="wide", page_title="Semantic Separation Visualization",
                   initial_sidebar_state="collapsed")
# Title
# -----------------------------
st.markdown("### Semantic Separation Visualization")

# -----------------------------
# Data loading
# -----------------------------
DEFAULT_PATH = "src/data/umap_df_for_js_plot_120825.csv"

df = None
if os.path.exists(DEFAULT_PATH):
    df = read_default_path(DEFAULT_PATH)
else:
    uploaded_file = st.file_uploader(
        "Upload a CSV/TSV/TXT", type=["csv", "tsv", "txt"])
    if uploaded_file is not None:
        df = read_uploaded_file(uploaded_file)

if df is None:
    st.info(
        f"Put your data file at `{DEFAULT_PATH}` (recommended), or upload a file above.")
    st.stop()

# -----------------------------
# Validate / filter expected columns
# -----------------------------
required_cols = {"UMAP1", "UMAP2", "SHOW_LABEL",
                 "SIL_SCORE", "SUBSET", "DISRUPTION"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"Missing required columns: {sorted(missing)}")
    st.stop()

df_filtered = df[df["DISRUPTION"].isin(
    DISRUPTION_ORDER) & df["SUBSET"].isin(SUBSET_ORDER)].copy()
df_filtered["SIL_SCORE"] = pd.to_numeric(
    df_filtered["SIL_SCORE"], errors="coerce")

# -----------------------------
# State
# -----------------------------
if "selected_cell" not in st.session_state or st.session_state.selected_cell is None:
    st.session_state.selected_cell = (
        SUBSET_ORDER[0], DISRUPTION_ORDER[0])  # (subset_key, disruption_key)

# -----------------------------
# Layout
# -----------------------------
PLOT_HEIGHT = 500
RIGHT_PANE_MAX_HEIGHT = PLOT_HEIGHT
LEGEND_MAX_HEIGHT = 170

left, right = st.columns([1.5, 1.0], gap="small")


# -----------------------------
# LEFT: Plot (MUST stay entirely inside this block)
# -----------------------------
with left:
    subset_key, disruption_key = st.session_state.selected_cell
    df_sel = df_filtered[
        (df_filtered["SUBSET"] == subset_key) &
        (df_filtered["DISRUPTION"] == disruption_key)
    ]

    st.markdown(
        f"**Selection:** {full(SUBSET_META, subset_key)} / {full(DISRUPTION_META, disruption_key)}")

    fig = make_umap_plot(df_sel)
    fig.update_layout(height=PLOT_HEIGHT, margin=dict(l=5, r=5, t=30, b=5))
    st.plotly_chart(fig, width="stretch")


# -----------------------------
# RIGHT: Grid + Legend (balanced wrappers only)
# -----------------------------
with right:

    grid_resp = render_silhouette_grid(
        df_filtered=df_filtered,
        subset_order=SUBSET_ORDER,
        disruption_order=DISRUPTION_ORDER,
        subset_meta=SUBSET_META,
        disruption_meta=DISRUPTION_META,
        selected_cell=st.session_state.selected_cell,
        transpose=True,     # rows=subsets, cols=disruptions (fits better)
        display="abbr",     # abbreviations in grid
        grid_height=400,      # autoHeight handles real height
        max_width_px=0,     # use container width
    )

    legend_iframe = render_legend_iframe_html(
        template_path="src/templates/legend.html",
        css_path="src/styles/app.css",
        show_colors=SHOW_COLORS,
        disruption_meta=DISRUPTION_LEGEND_META,
        disruption_order=DISRUPTION_ORDER,
        subset_meta=SUBSET_LEGEND_META,
        subset_order=SUBSET_LEGEND_ORDER,
    )

    components.html(legend_iframe, height=300, scrolling=True)

    # -----------------------------
    # Click handling (NEW grid writes OG keys; no mapping needed)
    # -----------------------------
    grid_data = grid_resp.get("data", None)

    if isinstance(grid_data, pd.DataFrame):
        df_grid = grid_data
    elif isinstance(grid_data, list):
        df_grid = pd.DataFrame(grid_data)
    else:
        df_grid = None

    if df_grid is not None and not df_grid.empty:
        if "__clicked_subset" in df_grid.columns and "__clicked_disruption" in df_grid.columns:
            df_clicked = df_grid[df_grid["__clicked_subset"].astype(
                str).str.len() > 0]
            if not df_clicked.empty:
                last = df_clicked.iloc[-1]
                clicked_subset = last.get("__clicked_subset")
                clicked_disruption = last.get("__clicked_disruption")

                if clicked_subset and clicked_disruption:
                    new_sel = (clicked_subset, clicked_disruption)
                    if new_sel != st.session_state.selected_cell:
                        st.session_state.selected_cell = new_sel
                        st.rerun()
