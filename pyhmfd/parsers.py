"""Column-type fixup functions for HMD, HFD, and HFC data frames.

These mirror the HMDparse(), HFDparse(), and HFCparse() functions in the
original R package HMDHFDplus (Riffe, Aburto et al.).
"""

from __future__ import annotations

import pandas as pd

from .utils import parse_age_column

# ---------------------------------------------------------------------------
# HMD
# ---------------------------------------------------------------------------

_HMD_INT_COLS = {"Year", "Cohort"}
_HMD_FLOAT_COLS = {"mx", "qx", "ax", "lx", "dx", "Lx", "Tx", "ex", "Rx"}


def hmd_parse(df: pd.DataFrame, item: str | None = None) -> pd.DataFrame:
    """Coerce HMD data frame columns to appropriate dtypes.

    - Age: strip '+', convert to Int64, add OpenInterval bool column.
    - Year/Cohort: Int64.
    - Numeric measures: float64.
    - Population files split '1-Jan' and '31-Dec' columns are preserved as-is.
    """
    df = df.copy()

    if "Age" in df.columns:
        df["Age"], df["OpenInterval"] = parse_age_column(df["Age"])

    for col in _HMD_INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in df.columns:
        if col in _HMD_FLOAT_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Population counts: columns like 'Female', 'Male', 'Total' are floats
    # when item starts with 'Pop' or 'Exposures'
    if item and (item.startswith("Pop") or item.startswith("Exposures")):
        for col in {"Female", "Male", "Total"} & set(df.columns):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# HFD
# ---------------------------------------------------------------------------

_HFD_INT_COLS = {"Year", "Cohort", "Age", "Parity"}
_HFD_FLOAT_COLS = {"ASFR", "ASFR1", "ASFR2", "ASFR3", "ASFR4", "ASFR5p",
                   "TFR", "MAC", "sdMAC", "Births", "Exposure"}


def hfd_parse(df: pd.DataFrame, item: str | None = None) -> pd.DataFrame:
    """Coerce HFD data frame columns to appropriate dtypes.

    - Age: strip '+'/'-', convert to Int64, add OpenInterval bool column.
    - Year/Cohort/Parity: Int64.
    - Rate/count columns: float64.
    """
    df = df.copy()

    if "Age" in df.columns:
        df["Age"], df["OpenInterval"] = parse_age_column(df["Age"])

    for col in _HFD_INT_COLS - {"Age"}:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    for col in df.columns:
        if col in _HFD_FLOAT_COLS or col.startswith("ASFR"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# HFC
# ---------------------------------------------------------------------------

def hfc_parse(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce HFC data frame columns to appropriate dtypes.

    HFC files have a different layout: Year1, Year2, AgeInterval columns
    plus various rate columns.
    """
    df = df.copy()

    for col in {"Year1", "Year2"}:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    if "AgeInterval" in df.columns:
        # Standardise 'w' (wide/open) label
        df["AgeInterval"] = df["AgeInterval"].astype(str).str.strip()
        df["OpenInterval"] = df["AgeInterval"].str.lower() == "w"

    for col in df.columns:
        if col not in {"Country", "Region", "AgeInterval", "OpenInterval",
                       "Year1", "Year2", "Collection", "Note"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
