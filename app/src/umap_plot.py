import plotly.express as px


def make_umap_plot(df_subset):
    # df_subset should already be filtered to the selected (SUBSET, DISRUPTION)
    fig = px.scatter(
        df_subset,
        x="UMAP1",
        y="UMAP2",
        color="SHOW_LABEL",
        hover_data=["SEASON", "EPISODE",
                    "SIL_SCORE", "SUBSET", "DISRUPTION"],
        title=None
    )
    fig.update_layout(showlegend=False)
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
    return fig
