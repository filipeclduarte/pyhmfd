"""pyhmfd — Read Human Mortality Database and Human Fertility Database data.

This package is a Python port of the R package HMDHFDplus by
Tim Riffe, Jose Manuel Aburto et al.
  Original R package: https://github.com/timriffe/HMDHFDplus
  License: GPL-2.0

Supported databases
-------------------
- Human Mortality Database (HMD) — https://www.mortality.org
- Human Fertility Database (HFD) — https://www.humanfertility.org
- Human Fertility Collection (HFC) — https://www.fertilitydata.org
- Japanese Mortality Database (JMD) — https://www.ipss.go.jp/p-toukei/JMD
- Canadian Historical Mortality Database (CHMD) — https://www.prdh.umontreal.ca/BDLC

Quick start
-----------
>>> import pyhmfd
>>> df = pyhmfd.read_hmd_web("USA", "Mx_1x1")          # needs HMD account
>>> df = pyhmfd.read_hfd_web("USA", "asfrRR")           # needs HFD account
>>> df = pyhmfd.read_jmd_web("01", "Deaths_1x1")        # no auth
>>> df = pyhmfd.read_chmd_web("qc", "Mx_1x1")           # no auth
>>> df = pyhmfd.read_hfc_web("RUS", "ASFRstand")        # no auth

Credentials
-----------
Set ``HMD_USER`` / ``HMD_PASSWORD`` (and ``HFD_USER`` / ``HFD_PASSWORD``)
environment variables, or pass them explicitly, or let the package prompt
interactively. Credentials can also be stored in the system keyring.
"""

from .chmd import read_chmd_web
from .hfc import get_hfc_countries, read_hfc_web
from .hfd import (
    get_hfd_countries,
    get_hfd_date,
    get_hfd_items,
    read_hfd,
    read_hfd_web,
)
from .hmd import (
    get_chmd_provinces,
    get_hmd_countries,
    get_hmd_items,
    get_jmd_prefectures,
    read_hmd,
    read_hmd_web,
)
from .jmd import read_jmd_web

__version__ = "0.1.2"
__all__ = [
    # HMD
    "read_hmd",
    "read_hmd_web",
    "get_hmd_countries",
    "get_hmd_items",
    # HFD
    "read_hfd",
    "read_hfd_web",
    "get_hfd_countries",
    "get_hfd_date",
    "get_hfd_items",
    # HFC
    "read_hfc_web",
    "get_hfc_countries",
    # JMD
    "read_jmd_web",
    "get_jmd_prefectures",
    # CHMD
    "read_chmd_web",
    "get_chmd_provinces",
]
