"""Human Mortality Database (HMD) reader and utilities.

Python port of readHMD(), readHMDweb(), getHMDcountries(), and
getHMDitemavail() from the R package HMDHFDplus
(Riffe, Aburto et al., https://github.com/timriffe/HMDHFDplus).
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

import pandas as pd

from .auth import resolve_credentials
from .parsers import hmd_parse
from .utils import check_response, read_table_from_text

_BASE = "https://www.mortality.org"
_LOGIN_URL = f"{_BASE}/Account/Login"

# ---------------------------------------------------------------------------
# Local file reader
# ---------------------------------------------------------------------------


def read_hmd(filepath: str, fixup: bool = True) -> pd.DataFrame:
    """Read a locally saved HMD text file into a DataFrame.

    Parameters
    ----------
    filepath:
        Path to the HMD ``.txt`` file (e.g. ``Mx_1x1.txt``).
    fixup:
        If True, run :func:`~pyhmd.parsers.hmd_parse` to coerce column
        types and add the ``OpenInterval`` indicator column.

    Returns
    -------
    pandas.DataFrame
    """
    with open(filepath, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    df = read_table_from_text(text)
    item = str(filepath).split("/")[-1].replace(".txt", "")
    return hmd_parse(df, item=item) if fixup else df


# ---------------------------------------------------------------------------
# Authenticated web reader
# ---------------------------------------------------------------------------


def _login(session: requests.Session, username: str, password: str) -> None:
    """Establish an authenticated HMD session (modifies *session* in-place)."""
    resp = session.get(_LOGIN_URL, timeout=30)
    check_response(resp, "HMD login page")

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
            f"HMD login failed (HTTP {resp.status_code}). "
            "Check your credentials at https://www.mortality.org"
        )


def read_hmd_web(
    country: str,
    item: str,
    username: str | None = None,
    password: str | None = None,
    fixup: bool = True,
) -> pd.DataFrame:
    """Download one data item for one country from the HMD.

    Parameters
    ----------
    country:
        HMD country short code (e.g. ``"USA"``, ``"FRATNP"``).
        Use :func:`get_hmd_countries` to list valid codes.
    item:
        Data item name (e.g. ``"Mx_1x1"``, ``"Deaths_1x1"``).
        Use :func:`get_hmd_items` to list available items per country.
    username:
        HMD account e-mail. Resolved from ``HMD_USER`` env var if omitted.
    password:
        HMD account password. Resolved from ``HMD_PASSWORD`` env var or
        keyring if omitted.
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.

    Returns
    -------
    pandas.DataFrame

    Examples
    --------
    >>> import pyhmd
    >>> df = pyhmd.read_hmd_web("USA", "Mx_1x1")
    """
    username, password = resolve_credentials(
        username, password,
        service="HMD",
        env_user="HMD_USER",
        env_pass="HMD_PASSWORD",
    )

    with requests.Session() as session:
        _login(session, username, password)

        url = f"{_BASE}/File/GetDocument/Files/{country}/STATS/{item}.txt"
        resp = session.get(url, timeout=60)
        check_response(resp, f"HMD {country}/{item}")

    df = read_table_from_text(resp.text)
    return hmd_parse(df, item=item) if fixup else df


# ---------------------------------------------------------------------------
# Country / item utilities
# ---------------------------------------------------------------------------


def get_hmd_countries() -> list[str]:
    """Return all HMD country and sub-population short codes.

    Returns
    -------
    list[str]
        e.g. ``['AUS', 'AUT', ..., 'USA']``
    """
    resp = requests.get(f"{_BASE}/Data/Countries", timeout=30)
    check_response(resp, "HMD country list")

    soup = BeautifulSoup(resp.text, "html.parser")
    codes: list[str] = []
    for a in soup.select("a[href*='/Country/']"):
        href = a["href"]
        code = href.rstrip("/").split("/")[-1]
        if code:
            codes.append(code)
    return sorted(set(codes))


def get_hmd_items(country: str) -> pd.DataFrame:
    """List all data items available for a given HMD country.

    Parameters
    ----------
    country:
        HMD country short code.

    Returns
    -------
    pandas.DataFrame
        Columns: ``item``, ``description``, ``url``.
    """
    url = f"{_BASE}/Country/GetData/{country}"
    resp = requests.get(url, timeout=30)
    check_response(resp, f"HMD items for {country}")

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    for a in soup.select("a[href*='.txt']"):
        href = a.get("href", "")
        if not href:
            continue
        item_name = href.rstrip("/").split("/")[-1].replace(".txt", "")
        rows.append({"item": item_name, "description": a.get_text(strip=True), "url": href})

    return pd.DataFrame(rows).drop_duplicates("item").reset_index(drop=True)


# ---------------------------------------------------------------------------
# JMD
# ---------------------------------------------------------------------------


def get_jmd_prefectures() -> dict[str, str]:
    """Return a mapping of Japanese prefecture name → 2-digit code.

    Codes run from ``'00'`` (all Japan) to ``'47'`` (Okinawa).

    Returns
    -------
    dict[str, str]
    """
    return {
        "All Japan": "00",
        "Hokkaido": "01", "Aomori": "02", "Iwate": "03", "Miyagi": "04",
        "Akita": "05", "Yamagata": "06", "Fukushima": "07", "Ibaraki": "08",
        "Tochigi": "09", "Gunma": "10", "Saitama": "11", "Chiba": "12",
        "Tokyo": "13", "Kanagawa": "14", "Niigata": "15", "Toyama": "16",
        "Ishikawa": "17", "Fukui": "18", "Yamanashi": "19", "Nagano": "20",
        "Gifu": "21", "Shizuoka": "22", "Aichi": "23", "Mie": "24",
        "Shiga": "25", "Kyoto": "26", "Osaka": "27", "Hyogo": "28",
        "Nara": "29", "Wakayama": "30", "Tottori": "31", "Shimane": "32",
        "Okayama": "33", "Hiroshima": "34", "Yamaguchi": "35", "Tokushima": "36",
        "Kagawa": "37", "Ehime": "38", "Kochi": "39", "Fukuoka": "40",
        "Saga": "41", "Nagasaki": "42", "Kumamoto": "43", "Oita": "44",
        "Miyazaki": "45", "Kagoshima": "46", "Okinawa": "47",
    }


# ---------------------------------------------------------------------------
# CHMD
# ---------------------------------------------------------------------------


def get_chmd_provinces() -> list[str]:
    """Return Canadian province codes for the CHMD.

    Returns
    -------
    list[str]
        e.g. ``['ab', 'bc', 'can', ...]``
    """
    return sorted([
        "can", "ab", "bc", "mb", "nb", "nl", "ns", "on", "pe", "qc", "sk",
    ])
