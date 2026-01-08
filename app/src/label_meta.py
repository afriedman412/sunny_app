# Keys must match what's in your dataframe (og labels)
DISRUPTION_META = {
    "RAW": {"full": "Raw", "abbr": "Raw"},
    "C":   {"full": "Clean", "abbr": "Clean"},
    "CS":  {"full": "Clean + Partial Shuffle", "abbr": "C+PS"},
    "CFS": {"full": "Clean + Full Shuffle", "abbr": "C+FS"},
    "SAP": {"full": "Shuffle and Preserve", "abbr": "SAP"},
}

DISRUPTION_LEGEND_META = {
    "RAW": {"full": "Unedited text", "abbr": "Raw"},
    "C":   {"full": "Capitalization and punctuation removed", "abbr": "Clean"},
    "CS":  {"full": "Cleaned and shuffled in 5 word increments", "abbr": "C+PS"},
    "CFS": {"full": "Clean and fully reordered", "abbr": "C+FS"},
    "SAP": {"full": "Reordered but relative capitalization and punctuation are preserved", "abbr": "SAP"},
}

SUBSET_META = {
    "Emotion": {"full": "Emotion", "abbr": "E"},
    "Toxicity": {"full": "Toxicity", "abbr": "Tx"},
    "Topics": {"full": "Topics", "abbr": "Tp"},
    "Emotion + Toxicity": {"full": "Emotion + Toxicity", "abbr": "E+Tx"},
    "Emotion + Topics": {"full": "Emotion + Topics", "abbr": "E+Tp"},
    "Topics + Toxicity": {"full": "Topics + Toxicity", "abbr": "Tp+Tx"},
    "Emotion + Topics + Toxicity": {"full": "Emotion + Topics + Toxicity", "abbr": "E+Tp+Tx"},
}

SUBSET_LEGEND_META = {
    "Emotion": {"full": "Emotion", "abbr": "E"},
    "Toxicity": {"full": "Toxicity", "abbr": "Tx"},
    "Topics": {"full": "Topics", "abbr": "Tp"},
}

DISRUPTION_ORDER = ["RAW", "C", "CS", "CFS", "SAP"]

SUBSET_ORDER = [
    "Emotion", "Toxicity", "Topics",
    "Emotion + Toxicity", "Emotion + Topics",
    "Topics + Toxicity", "Emotion + Topics + Toxicity",
]

SUBSET_LEGEND_ORDER = ["Emotion", "Toxicity", "Topics"]

SHOW_COLORS = {
    "South Park": "#fe2b2b",
    "Always Sunny": "#0368c9",
    "The Office": "#84c8ff",
}


def full(meta: dict, key: str) -> str:
    return meta.get(key, {}).get("full", key)


def abbr(meta: dict, key: str) -> str:
    return meta.get(key, {}).get("abbr", key)


DISRUPTION_ABBR_TO_KEY = {
    abbr(DISRUPTION_META, k): k for k in DISRUPTION_ORDER}
SUBSET_ABBR_TO_KEY = {abbr(SUBSET_META, k): k for k in SUBSET_ORDER}
