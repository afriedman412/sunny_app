import pandas as pd


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".tsv") or name.endswith(".txt"):
        return pd.read_csv(uploaded_file, sep="\t")
    return pd.read_csv(uploaded_file)


def read_default_path(path: str) -> pd.DataFrame:
    # Streamlit runs from the project root; keep your default CSV there or use an absolute path.
    return pd.read_csv(path)
