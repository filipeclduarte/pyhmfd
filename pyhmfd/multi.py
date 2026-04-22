"""Multi-country download utilities for HMD and HFD.

Downloads data for multiple countries in parallel, reusing a single
authenticated HTTP session and returning a concatenated DataFrame.
"""

from __future__ import annotations

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

import pandas as pd
import requests

from .auth import resolve_credentials
from .hfd import _BASE as HFD_BASE
from .hfd import _LOGIN_URL as HFD_LOGIN_URL
from .hfd import _login as hfd_login
from .hfd import get_hfd_countries, get_hfd_date
from .hmd import _BASE as HMD_BASE
from .hmd import _LOGIN_URL as HMD_LOGIN_URL
from .hmd import _login as hmd_login
from .hmd import get_hmd_countries
from .parsers import hfd_parse, hmd_parse
from .utils import check_response, read_table_from_text


# ---------------------------------------------------------------------------
# Internal per-country workers (run inside thread pool)
# ---------------------------------------------------------------------------


def _fetch_hmd(
    session: requests.Session,
    country: str,
    item: str,
    fixup: bool,
) -> tuple[str, pd.DataFrame]:
    url = f"{HMD_BASE}/File/GetDocument/hmd.v6/{country}/STATS/{item}.txt"
    resp = session.get(url, timeout=60)
    check_response(resp, f"HMD {country}/{item}")
    df = read_table_from_text(resp.text)
    if fixup:
        df = hmd_parse(df, item=item)
    df.insert(0, "country", country)
    return country, df


def _fetch_hfd(
    session: requests.Session,
    country: str,
    item: str,
    fixup: bool,
) -> tuple[str, pd.DataFrame]:
    update_date = get_hfd_date(country)
    url = (
        f"{HFD_BASE}/File/GetDocument/Files/{country}/{update_date}/"
        f"{country}{item}.txt"
    )
    resp = session.get(url, timeout=60)
    check_response(resp, f"HFD {country}/{item}")
    df = read_table_from_text(resp.text)
    if fixup:
        df = hfd_parse(df, item=item)
    df.insert(0, "country", country)
    return country, df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def read_hmd_web_multi(
    countries: list[str] | Literal["all"],
    item: str,
    username: str | None = None,
    password: str | None = None,
    fixup: bool = True,
    workers: int = 4,
    on_error: Literal["warn", "raise"] = "warn",
) -> pd.DataFrame:
    """Download one HMD data item for multiple countries in parallel.

    Parameters
    ----------
    countries:
        List of HMD country short codes, or ``"all"`` to download every
        available country. Use :func:`~pyhmfd.get_hmd_countries` to list
        valid codes.
    item:
        Data item name (e.g. ``"Mx_1x1"``, ``"Deaths_1x1"``).
    username:
        HMD account e-mail. Resolved from ``HMD_USER`` env var if omitted.
    password:
        HMD account password. Resolved from ``HMD_PASSWORD`` env var or
        keyring if omitted.
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.
    workers:
        Number of parallel download threads.
    on_error:
        ``"warn"`` (default) — skip failing countries and emit a warning.
        ``"raise"`` — raise the first error encountered.

    Returns
    -------
    pandas.DataFrame
        Concatenated data with a leading ``country`` column.

    Examples
    --------
    >>> import pyhmfd
    >>> df = pyhmfd.read_hmd_web_multi(["AUS", "USA", "SWE"], "Mx_1x1")
    >>> df = pyhmfd.read_hmd_web_multi("all", "Deaths_1x1", workers=8)
    """
    username, password = resolve_credentials(
        username, password,
        service="HMD",
        env_user="HMD_USER",
        env_pass="HMD_PASSWORD",
    )

    if countries == "all":
        countries = get_hmd_countries()

    results: dict[str, pd.DataFrame] = {}
    errors: dict[str, Exception] = {}

    with requests.Session() as session:
        hmd_login(session, username, password)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_fetch_hmd, session, c, item, fixup): c
                for c in countries
            }
            for future in as_completed(futures):
                country = futures[future]
                try:
                    _, df = future.result()
                    results[country] = df
                except Exception as exc:
                    if on_error == "raise":
                        raise
                    errors[country] = exc

    if errors:
        msg = "\n".join(f"  {c}: {e}" for c, e in errors.items())
        warnings.warn(
            f"Failed to download {len(errors)} country/countries:\n{msg}",
            stacklevel=2,
        )

    if not results:
        raise RuntimeError("No data was successfully downloaded.")

    combined = pd.concat(results.values(), ignore_index=True)
    sort_cols = [c for c in ["country", "Year", "Age"] if c in combined.columns]
    return combined.sort_values(sort_cols).reset_index(drop=True)


def read_hfd_web_multi(
    countries: list[str] | Literal["all"],
    item: str,
    username: str | None = None,
    password: str | None = None,
    fixup: bool = True,
    workers: int = 4,
    on_error: Literal["warn", "raise"] = "warn",
) -> pd.DataFrame:
    """Download one HFD data item for multiple countries in parallel.

    Parameters
    ----------
    countries:
        List of HFD country short codes, or ``"all"`` to download every
        available country. Use :func:`~pyhmfd.get_hfd_countries` to list
        valid codes.
    item:
        Data product code (e.g. ``"asfrRR"``, ``"mabRR"``).
    username:
        HFD account e-mail. Resolved from ``HFD_USER`` env var if omitted.
    password:
        HFD account password. Resolved from ``HFD_PASSWORD`` env var or
        keyring if omitted.
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.
    workers:
        Number of parallel download threads.
    on_error:
        ``"warn"`` (default) — skip failing countries and emit a warning.
        ``"raise"`` — raise the first error encountered.

    Returns
    -------
    pandas.DataFrame
        Concatenated data with a leading ``country`` column.

    Examples
    --------
    >>> import pyhmfd
    >>> df = pyhmfd.read_hfd_web_multi(["USA", "SWE", "JPN"], "asfrRR")
    >>> df = pyhmfd.read_hfd_web_multi("all", "asfrRR", workers=6)
    """
    username, password = resolve_credentials(
        username, password,
        service="HFD",
        env_user="HFD_USER",
        env_pass="HFD_PASSWORD",
    )

    if countries == "all":
        countries = get_hfd_countries()["code"].tolist()

    results: dict[str, pd.DataFrame] = {}
    errors: dict[str, Exception] = {}

    with requests.Session() as session:
        hfd_login(session, username, password)

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_fetch_hfd, session, c, item, fixup): c
                for c in countries
            }
            for future in as_completed(futures):
                country = futures[future]
                try:
                    _, df = future.result()
                    results[country] = df
                except Exception as exc:
                    if on_error == "raise":
                        raise
                    errors[country] = exc

    if errors:
        msg = "\n".join(f"  {c}: {e}" for c, e in errors.items())
        warnings.warn(
            f"Failed to download {len(errors)} country/countries:\n{msg}",
            stacklevel=2,
        )

    if not results:
        raise RuntimeError("No data was successfully downloaded.")

    combined = pd.concat(results.values(), ignore_index=True)
    sort_cols = [c for c in ["country", "Year", "Age"] if c in combined.columns]
    return combined.sort_values(sort_cols).reset_index(drop=True)
