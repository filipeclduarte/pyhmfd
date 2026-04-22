"""Canadian Historical Mortality Database (CHMD) reader.

Python port of readCHMDweb() from the R package HMDHFDplus
(Riffe, Aburto et al., https://github.com/timriffe/HMDHFDplus).
"""

from __future__ import annotations

import requests

import pandas as pd

from .parsers import hmd_parse
from .utils import check_response, read_table_from_text

_BASE = "https://www.prdh.umontreal.ca/BDLC/data"


def read_chmd_web(
    prov_id: str = "can",
    item: str = "Deaths_1x1",
    fixup: bool = True,
) -> pd.DataFrame:
    """Download data for a Canadian province from the CHMD.

    No authentication is required.

    Parameters
    ----------
    prov_id:
        Province short code (``'can'`` = all Canada, ``'qc'`` = Quebec, …).
        Use :func:`~pyhmd.hmd.get_chmd_provinces` to list all codes.
    item:
        Data item name (e.g. ``'Deaths_1x1'``, ``'Mx_1x1'``).
    fixup:
        If True, coerce column types and add ``OpenInterval`` column.

    Returns
    -------
    pandas.DataFrame

    Examples
    --------
    >>> import pyhmd
    >>> df = pyhmd.read_chmd_web("qc", "Mx_1x1")
    """
    url = f"{_BASE}/{prov_id}/{item}.txt"
    resp = requests.get(url, timeout=60)
    check_response(resp, f"CHMD prov={prov_id} item={item}")

    df = read_table_from_text(resp.text)
    return hmd_parse(df, item=item) if fixup else df
