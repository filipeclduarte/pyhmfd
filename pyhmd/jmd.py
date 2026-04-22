"""Japanese Mortality Database (JMD) reader.

Python port of readJMDweb() from the R package HMDHFDplus
(Riffe, Aburto et al., https://github.com/timriffe/HMDHFDplus).
"""

from __future__ import annotations

import requests

import pandas as pd

from .parsers import hmd_parse
from .utils import check_response, read_table_from_text

_BASE = "https://www.ipss.go.jp/p-toukei/JMD"


def read_jmd_web(
    pref_id: str = "00",
    item: str = "Deaths_5x5",
    fixup: bool = True,
) -> pd.DataFrame:
    """Download data for a Japanese prefecture from the JMD.

    No authentication is required.

    Parameters
    ----------
    pref_id:
        Two-digit prefecture code (``'00'`` = all Japan, ``'01'`` = Hokkaido,
        …, ``'47'`` = Okinawa).
        Use :func:`~pyhmd.hmd.get_jmd_prefectures` to list all codes.
    item:
        Data item name (e.g. ``'Deaths_5x5'``, ``'Mx_1x1'``).
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.

    Returns
    -------
    pandas.DataFrame

    Examples
    --------
    >>> import pyhmd
    >>> df = pyhmd.read_jmd_web("01", "Deaths_1x1")
    """
    url = f"{_BASE}/{pref_id}/STATS/{item}.txt"
    resp = requests.get(url, timeout=60)
    check_response(resp, f"JMD pref={pref_id} item={item}")

    df = read_table_from_text(resp.text)
    return hmd_parse(df, item=item) if fixup else df
