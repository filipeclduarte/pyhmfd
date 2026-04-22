"""Shared helpers for age column cleaning and open-interval detection."""

from __future__ import annotations

import io

import pandas as pd
import requests


def parse_age_column(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Strip trailing '+' and leading/trailing '-' from age strings.

    Returns (age_int, open_interval) where open_interval is True for the
    terminal open-ended age group (e.g. '110+').
    """
    s = series.astype(str).str.strip()
    open_interval = s.str.endswith("+")
    # Remove '+' suffix and trailing '-' range indicator (not an open interval)
    s = s.str.replace(r"[+]$", "", regex=True)
    s = s.str.replace(r"[-]$", "", regex=True)
    age_int = pd.to_numeric(s, errors="coerce").astype("Int64")
    return age_int, open_interval


def read_table_from_text(text: str, **kwargs) -> pd.DataFrame:
    """Parse a fixed-width demographic text table (skip=2, na='.').

    All HMD/HFD files share the same format: two header lines then
    whitespace-delimited data with '.' for missing values.
    """
    defaults = dict(sep=r"\s+", skiprows=2, na_values=".", engine="python")
    defaults.update(kwargs)
    return pd.read_csv(io.StringIO(text), **defaults)


def check_response(
    response: requests.Response,
    label: str = "request",
    expect_html: bool = False,
) -> None:
    """Raise a descriptive error if the HTTP response signals a problem.

    Parameters
    ----------
    expect_html:
        Set True for login/page requests where HTML is the expected content
        type. When False (default), receiving HTML is treated as an auth error.
    """
    if response.status_code != 200:
        raise ConnectionError(
            f"{label} failed with HTTP {response.status_code}: {response.url}"
        )
    if not expect_html:
        ct = response.headers.get("Content-Type", "")
        if "text/html" in ct and "<!DOCTYPE" in response.text[:200]:
            raise PermissionError(
                "Server returned an HTML page instead of data. "
                "Authentication may have failed — check your credentials."
            )
