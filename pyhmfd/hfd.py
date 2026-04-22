"""Human Fertility Database (HFD) reader and utilities.

Python port of readHFD(), readHFDweb(), getHFDcountries(), getHFDdate(),
and getHFDitemavail() from the R package HMDHFDplus
(Riffe, Aburto et al., https://github.com/timriffe/HMDHFDplus).
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

import pandas as pd

from .auth import resolve_credentials
from .parsers import hfd_parse
from .utils import check_response, read_table_from_text

_BASE = "https://www.humanfertility.org"
_LOGIN_URL = f"{_BASE}/Account/Login"

# ---------------------------------------------------------------------------
# Local file reader
# ---------------------------------------------------------------------------


def read_hfd(filepath: str, fixup: bool = True, item: str | None = None) -> pd.DataFrame:
    """Read a locally saved HFD text file into a DataFrame.

    Parameters
    ----------
    filepath:
        Path to the HFD ``.txt`` file.
    fixup:
        If True, run :func:`~pyhmfd.parsers.hfd_parse` to coerce column
        types and add the ``OpenInterval`` indicator column.
    item:
        Data product code (e.g. ``"mabRR"``). Used by the parser to
        determine column types when ``fixup=True``.

    Returns
    -------
    pandas.DataFrame
    """
    if item is None:
        item = str(filepath).split("/")[-1].replace(".txt", "")
    with open(filepath, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    df = read_table_from_text(text)
    return hfd_parse(df, item=item) if fixup else df


# ---------------------------------------------------------------------------
# Authenticated web reader
# ---------------------------------------------------------------------------


def _login(session: requests.Session, username: str, password: str) -> None:
    """Establish an authenticated HFD session (modifies *session* in-place)."""
    resp = session.get(_LOGIN_URL, timeout=30)
    check_response(resp, "HFD login page", expect_html=True)

    soup = BeautifulSoup(resp.text, "html.parser")
    token_tag = soup.find("input", {"name": "__RequestVerificationToken"})
    token = token_tag["value"] if token_tag else ""

    payload = {
        "Email": username,
        "Password": password,
        "__RequestVerificationToken": token,
    }
    resp = session.post(_LOGIN_URL, data=payload, timeout=30)
    if resp.status_code not in (200, 302):
        raise PermissionError(
            f"HFD login failed (HTTP {resp.status_code}). "
            "Check your credentials at https://www.humanfertility.org"
        )


def read_hfd_web(
    country: str,
    item: str,
    username: str | None = None,
    password: str | None = None,
    fixup: bool = True,
) -> pd.DataFrame:
    """Download one data item for one country from the HFD.

    Parameters
    ----------
    country:
        HFD country short code (e.g. ``"USA"``, ``"FRATNP"``).
        Use :func:`get_hfd_countries` to list valid codes.
    item:
        Data product code (e.g. ``"asfrRR"``, ``"mabRR"``).
        Use :func:`get_hfd_items` to list available items per country.
    username:
        HFD account e-mail. Resolved from ``HFD_USER`` env var if omitted.
    password:
        HFD account password. Resolved from ``HFD_PASSWORD`` env var or
        keyring if omitted.
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.

    Returns
    -------
    pandas.DataFrame

    Examples
    --------
    >>> import pyhmfd
    >>> df = pyhmfd.read_hfd_web("USA", "asfrRR")
    """
    username, password = resolve_credentials(
        username, password,
        service="HFD",
        env_user="HFD_USER",
        env_pass="HFD_PASSWORD",
    )

    update_date = get_hfd_date(country)

    with requests.Session() as session:
        _login(session, username, password)

        url = (
            f"{_BASE}/File/GetDocument/Files/{country}/{update_date}/"
            f"{country}{item}.txt"
        )
        resp = session.get(url, timeout=60)
        check_response(resp, f"HFD {country}/{item}")

    df = read_table_from_text(resp.text)
    return hfd_parse(df, item=item) if fixup else df


# ---------------------------------------------------------------------------
# Country / date / item utilities
# ---------------------------------------------------------------------------


def get_hfd_countries() -> pd.DataFrame:
    """Return a DataFrame of all HFD countries.

    Returns
    -------
    pandas.DataFrame
        Columns: ``country`` (full name), ``code`` (short code).
    """
    resp = requests.get(f"{_BASE}/Data/Countries", timeout=30)
    check_response(resp, "HFD country list", expect_html=True)

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for a in soup.select("a[href*='cntr=']"):
        href = a.get("href", "")
        code = href.split("cntr=")[-1].strip()
        name = a.get_text(strip=True)
        if code and name:
            rows.append({"country": name, "code": code})
    return pd.DataFrame(rows).drop_duplicates("code").reset_index(drop=True)


def _country_page_url(country: str) -> str:
    return f"{_BASE}/Country/Country?cntr={country}"


def get_hfd_date(country: str) -> str:
    """Return the last-update date for a given HFD country.

    Parameters
    ----------
    country:
        HFD country short code.

    Returns
    -------
    str
        Eight-digit date string in ``'YYYYMMDD'`` format.
    """
    resp = requests.get(_country_page_url(country), timeout=30)
    check_response(resp, f"HFD date for {country}", expect_html=True)

    soup = BeautifulSoup(resp.text, "html.parser")
    # Date appears in download links: /File/GetDocument/Files/USA/20260323/USAasfrRR.txt
    # The server may use backslashes in hrefs — normalise them first
    for a in soup.select("a[href*='.txt']"):
        href = a.get("href", "").replace("\\", "/")
        parts = href.split("/")
        for part in parts:
            if len(part) == 8 and part.isdigit():
                return part
    raise ValueError(f"Could not determine update date for HFD country '{country}'")


def get_hfd_items(country: str) -> pd.DataFrame:
    """List all data items available for a given HFD country.

    Parameters
    ----------
    country:
        HFD country short code.

    Returns
    -------
    pandas.DataFrame
        Columns: ``item``, ``description``, ``url``.
    """
    resp = requests.get(_country_page_url(country), timeout=30)
    check_response(resp, f"HFD items for {country}", expect_html=True)

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for a in soup.select("a[href*='.txt']"):
        href = a.get("href", "").replace("\\", "/")
        if not href:
            continue
        filename = href.rstrip("/").split("/")[-1].replace(".txt", "")
        item_code = filename.replace(country, "", 1)
        rows.append({"item": item_code, "description": a.get_text(strip=True), "url": href})

    return pd.DataFrame(rows).drop_duplicates("item").reset_index(drop=True)
