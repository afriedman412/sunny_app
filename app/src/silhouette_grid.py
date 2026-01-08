# src/silhouette_grid.py

from __future__ import annotations

import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
from st_aggrid import ColumnsAutoSizeMode


def _label(meta: dict[str, dict], key: str, kind: str) -> str:
    """kind in {'full','abbr'}; falls back to key."""
    try:
        v = meta.get(key, {})
        return v.get(kind, key) or key
    except Exception:
        return key


def render_silhouette_grid(
    df_filtered: pd.DataFrame,
    subset_order: list[str],
    disruption_order: list[str],
    subset_meta: dict[str, dict],
    disruption_meta: dict[str, dict],
    *,
    transpose: bool = True,
    display: str = "abbr",  # 'abbr' or 'full'
    grid_height: int = 1,   # autoHeight will handle real height; keep >=1
    max_width_px: int = 0,  # 0 => 100% of container
    # (subset_key, disruption_key)
    selected_cell: tuple[str, str] | None = None,
):
    """
    Silhouette grid with:
      - Optional transpose (default True): rows=subsets, cols=disruptions (fits better)
      - Label meta system: {og: {'full':..., 'abbr':...}}
      - Display abbreviations in grid (or full) without changing underlying keys
      - True cell click: stores OG keys into __clicked_subset/__clicked_disruption
      - Rounded values to 3 decimals
      - Gradient cell backgrounds
      - Centered/wrapped headers
      - Filter/sort/menu disabled
      - Auto height to data length (no dead space)
    """

    # -----------------------------
    # Label maps (display only)
    # -----------------------------
    subset_disp = {k: _label(subset_meta, k, display) for k in subset_order}
    disruption_disp = {k: _label(disruption_meta, k, display)
                       for k in disruption_order}

    # -----------------------------
    # Build pivot in OG keys
    # -----------------------------
    if transpose:
        # rows = SUBSET (OG), cols = DISRUPTION (OG)
        pivot = (
            df_filtered.pivot_table(
                index="SUBSET",
                columns="DISRUPTION",
                values="SIL_SCORE",
                aggfunc="first",
            )
            .reindex(subset_order)
            .reindex(columns=disruption_order)
            .reset_index()
        )
        # keep OG subset key, but display label in a separate column
        pivot["__subset_key"] = pivot["SUBSET"]
        pivot["SUBSET"] = pivot["SUBSET"].map(
            subset_disp).fillna(pivot["SUBSET"])

        row_label_field = "SUBSET"            # display
        row_key_field = "__subset_key"        # OG key
        col_key_order = disruption_order      # OG keys
        col_header_map = disruption_disp      # OG -> display

    else:
        # rows = DISRUPTION (OG), cols = SUBSET (OG)
        pivot = (
            df_filtered.pivot_table(
                index="DISRUPTION",
                columns="SUBSET",
                values="SIL_SCORE",
                aggfunc="first",
            )
            .reindex(disruption_order)
            .reindex(columns=subset_order)
            .reset_index()
        )
        pivot["__disruption_key"] = pivot["DISRUPTION"]
        pivot["DISRUPTION"] = pivot["DISRUPTION"].map(
            disruption_disp).fillna(pivot["DISRUPTION"])

        row_label_field = "DISRUPTION"
        row_key_field = "__disruption_key"
        col_key_order = subset_order
        col_header_map = subset_disp

    # round numeric columns to 3 decimals
    for c in col_key_order:
        if c in pivot.columns:
            pivot[c] = pd.to_numeric(pivot[c], errors="coerce").round(3)

    # click markers (OG keys)
    pivot["__clicked_subset"] = ""
    pivot["__clicked_disruption"] = ""

    # -----------------------------
    # Gradient bounds
    # -----------------------------
    vals = pd.to_numeric(df_filtered["SIL_SCORE"], errors="coerce").dropna()
    vmin = float(vals.min()) if len(vals) else 0.0
    vmax = float(vals.max()) if len(vals) else 1.0

    selected_subset_key = selected_cell[0] if selected_cell else None
    selected_disruption_key = selected_cell[1] if selected_cell else None

    # -----------------------------
    # Cell renderer captures click -> writes OG keys to hidden columns
    # We keep column field = OG key always, even if header shows abbreviation.
    # -----------------------------
    ClickCaptureRenderer = JsCode(
        f"""
        class ClickCaptureRenderer {{
          init(params) {{
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.style.cursor = 'pointer';
            this.eGui.style.userSelect = 'none';
            this.refresh(params);
          }}

          getGui() {{ return this.eGui; }}

          refresh(params) {{
            this.params = params;

            // display value
            const v = params.value;
            if (v === null || v === undefined || v === "") {{
              this.eGui.textContent = "";
            }} else if (typeof v === "number") {{
              this.eGui.textContent = v.toFixed(3);
            }} else {{
              this.eGui.textContent = String(v);
            }}

            this.eGui.onclick = () => {{
              const transpose = {str(transpose).lower()};

              // column field is ALWAYS OG key (subset or disruption depending on orientation)
              const colKey = params.colDef.field;

              // rowKey is stored in hidden field on the row
              const rowKey = params.data["{row_key_field}"];

              const subsetKey = transpose ? rowKey : colKey;
              const disruptionKey = transpose ? colKey : rowKey;

              params.node.setDataValue("__clicked_subset", subsetKey);
              params.node.setDataValue("__clicked_disruption", disruptionKey);
            }};

            return true;
          }}
        }}
        """
    )

    # -----------------------------
    # Gradient style + selected outline
    # Uses OG keys for correctness (not display labels)
    # -----------------------------
    cell_style = JsCode(
        f"""
        function(params) {{
          const col = params.colDef.field;

          // hide internal cols (if they ever render)
          if (col === "{row_key_field}" || col === "__clicked_subset" || col === "__clicked_disruption") {{
            return {{ display: "none" }};
          }}

          // style row label column
          if (col === "{row_label_field}") {{
            return {{ fontWeight: "600" }};
          }}

          const v = params.value;
          if (v === null || v === undefined || v === "") return {{ opacity: 0.55 }};

          const vmin = {vmin};
          const vmax = {vmax};
          const t = (vmax === vmin) ? 0.5 : (v - vmin) / (vmax - vmin);

          let r, g, b;
          if (t < 0.5) {{
            r = 255;
            g = Math.round(255 * t * 2);
            b = 0;
          }} else {{
            r = Math.round(255 * (1 - (t - 0.5) * 2));
            g = 255;
            b = 0;
          }}

          let style = {{
            backgroundColor: `rgb(${{r}},${{g}},${{b}})`,
            color: "#111",
            fontWeight: "600",
            textAlign: "center",
            borderRadius: "6px",
          }};

          // selected outline (compare OG keys)
          const transpose = {str(transpose).lower()};
          const selSubset = {("null" if selected_subset_key is None else repr(selected_subset_key))};
          const selDisruption = {("null" if selected_disruption_key is None else repr(selected_disruption_key))};

          if (selSubset !== null && selDisruption !== null) {{
            const colKey = params.colDef.field;          // OG column key
            const rowKey = params.data["{row_key_field}"]; // OG row key

            const subsetKey = transpose ? rowKey : colKey;
            const disruptionKey = transpose ? colKey : rowKey;

            if (subsetKey === selSubset && disruptionKey === selDisruption) {{
              style.boxShadow = "inset 0 0 0 3px rgba(0,0,0,0.55), 0 0 0 1px rgba(255,255,255,0.55)";
              style.filter = "brightness(0.92) saturate(1.05)";
              style.borderRadius = "8px";
            }}
          }}

          return style;
        }}
        """
    )

    # -----------------------------
    # Grid options (no filters/menus/sorting)
    # -----------------------------
    gb = GridOptionsBuilder.from_dataframe(pivot)

    gb.configure_default_column(
        resizable=True,
        sortable=False,
        filter=False,
        editable=False,
        suppressMenu=True,
        floatingFilter=False,
        wrapText=True,
        autoHeight=False,
    )
    HEADER_H = 46
    ROW_H = 32
    gb.configure_grid_options(
        headerHeight=HEADER_H,
        rowHeight=ROW_H,
        suppressMovableColumns=True,
        suppressRowClickSelection=True,
        suppressContextMenu=True,
        suppressMenuHide=True,
        sideBar=False,
    )

    # Row label column (display)
    gb.configure_column(row_label_field, pinned="left", width=190)

    # Internal key column (hidden)
    gb.configure_column(row_key_field, hide=True)
    gb.configure_column("__clicked_subset", hide=True)
    gb.configure_column("__clicked_disruption", hide=True)

    # Data columns: field stays OG key, headerName is display label
    for k in col_key_order:
        if k in pivot.columns:
            gb.configure_column(
                k,  # field = OG key
                header_name=col_header_map.get(k, k),
                width=92,
                sortable=False,
                filter=False,
                suppressMenu=True,
                editable=False,
                headerClass="sil-header-center",
                wrapHeaderText=True,
                autoHeaderHeight=True,
                valueFormatter="(value == null || isNaN(value)) ? '' : value.toFixed(3)",
                cellStyle=cell_style,
                cellRenderer=ClickCaptureRenderer,
            )

    grid_options = gb.build()

    n_rows = len(pivot)
    # +2 rows worth of padding to account for borders/header rounding differences across themes
    computed_height = HEADER_H + (n_rows * ROW_H) + 5
    return AgGrid(
        pivot,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,  # click updates row data
        height=computed_height,
        allow_unsafe_jscode=True,
        theme="streamlit",
        fit_columns_on_grid_load=True,
    )
