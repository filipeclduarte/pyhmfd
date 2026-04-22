"""Human Fertility Collection (HFC) reader.

Python port of readHFCweb() and getHFCcountries() from the R package
HMDHFDplus (Riffe, Aburto et al., https://github.com/timriffe/HMDHFDplus).
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

import pandas as pd

from .parsers import hfc_parse
from .utils import check_response, read_table_from_text

_BASE = "https://www.fertilitydata.org"


def read_hfc_web(
    country: str,
    item: str,
    fixup: bool = True,
) -> pd.DataFrame:
    """Download a data item for a country from the HFC.

    No authentication is required.

    Parameters
    ----------
    country:
        HFC population short code. Use :func:`get_hfc_countries` to list
        available codes.
    item:
        Data item identifier (e.g. ``'ASFRstand'``).
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.

    Returns
    -------
    pandas.DataFrame

    Examples
    --------
    >>> import pyhmd
    >>> df = pyhmd.read_hfc_web("RUS", "ASFRstand")
    """
    url = f"{_BASE}/data/{country}/{item}.txt"
    resp = requests.get(url, timeout=60)
    check_response(resp, f"HFC {country}/{item}")

    df = read_table_from_text(resp.text)
    return hfc_parse(df) if fixup else df


def get_hfc_countries(names: bool = False) -> list[str] | pd.DataFrame:
    """Return HFC population codes (and optionally full names).

    Parameters
    ----------
    names:
        If False (default), return a sorted list of short codes.
        If True, return a DataFrame with columns ``country`` and ``code``.

    Returns
    -------
    list[str] or pandas.DataFrame
    """
    resp = requests.get(f"{_BASE}/data/", timeout=30)
    check_response(resp, "HFC country list")

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if href.endswith("/") and len(href.strip("/")) >= 2:
            code = href.strip("/")
            name = a.get_text(strip=True)
            if code and name and code != "..":
                rows.append({"country": name, "code": code})

    df = pd.DataFrame(rows).drop_duplicates("code").reset_index(drop=True)
    if names:
        return df
    return sorted(df["code"].tolist())
