"""Tests for multi-country download functions."""

import warnings

import pandas as pd
import pytest
import responses as resp_lib

import pyhmfd
from pyhmfd.hmd import _BASE as HMD_BASE, _LOGIN_URL as HMD_LOGIN_URL
from pyhmfd.hfd import _BASE as HFD_BASE, _LOGIN_URL as HFD_LOGIN_URL, _country_page_url

_LOGIN_HTML = """\
<html><form>
<input name="__RequestVerificationToken" value="tok"/>
</form></html>
"""

_HMD_DATA = """\
Deaths, {country}, 1x1 (period 1x1), Last modified: 01-Jan-2024

   Age   Female    Male    Total
     0  1000.00  1100.0  2100.0
   110+     1.00     2.0      3.0
"""

_HFD_DATA = """\
Age-specific fertility rates, {country}, period
Last modified: 01-Jan-2024
Age    ASFR   Exposure
12    0.001   5000.0
55+       .   3000.0
"""

_HFD_COUNTRY_PAGE = """\
<html><body>
<a href="/File/GetDocument/Files/{country}/20260101/{country}asfrRR.txt">ASFR</a>
</body></html>
"""


def _register_hmd_country(country):
    resp_lib.add(
        resp_lib.GET,
        f"{HMD_BASE}/File/GetDocument/hmd.v6/{country}/STATS/Mx_1x1.txt",
        body=_HMD_DATA.format(country=country),
        status=200,
        content_type="text/plain",
    )


def _register_hfd_country(country):
    resp_lib.add(
        resp_lib.GET,
        _country_page_url(country),
        body=_HFD_COUNTRY_PAGE.format(country=country),
        status=200,
        content_type="text/html",
    )
    resp_lib.add(
        resp_lib.GET,
        f"{HFD_BASE}/File/GetDocument/Files/{country}/20260101/{country}asfrRR.txt",
        body=_HFD_DATA.format(country=country),
        status=200,
        content_type="text/plain",
    )


# ---------------------------------------------------------------------------
# HMD multi
# ---------------------------------------------------------------------------


@resp_lib.activate
def test_read_hmd_web_multi_two_countries():
    resp_lib.add(resp_lib.GET, HMD_LOGIN_URL, body=_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, HMD_LOGIN_URL, body="", status=200)
    _register_hmd_country("AUS")
    _register_hmd_country("USA")

    df = pyhmfd.read_hmd_web_multi(["AUS", "USA"], "Mx_1x1",
                                   username="u", password="p")

    assert "country" in df.columns
    assert set(df["country"].unique()) == {"AUS", "USA"}
    assert "OpenInterval" in df.columns


@resp_lib.activate
def test_read_hmd_web_multi_on_error_warn():
    resp_lib.add(resp_lib.GET, HMD_LOGIN_URL, body=_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, HMD_LOGIN_URL, body="", status=200)
    _register_hmd_country("AUS")
    # SWE will 404
    resp_lib.add(
        resp_lib.GET,
        f"{HMD_BASE}/File/GetDocument/hmd.v6/SWE/STATS/Mx_1x1.txt",
        status=404,
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        df = pyhmfd.read_hmd_web_multi(["AUS", "SWE"], "Mx_1x1",
                                       username="u", password="p",
                                       on_error="warn")
    assert any("SWE" in str(warning.message) for warning in w)
    assert set(df["country"].unique()) == {"AUS"}


@resp_lib.activate
def test_read_hmd_web_multi_on_error_raise():
    resp_lib.add(resp_lib.GET, HMD_LOGIN_URL, body=_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, HMD_LOGIN_URL, body="", status=200)
    resp_lib.add(
        resp_lib.GET,
        f"{HMD_BASE}/File/GetDocument/hmd.v6/XXX/STATS/Mx_1x1.txt",
        status=404,
    )

    with pytest.raises(ConnectionError):
        pyhmfd.read_hmd_web_multi(["XXX"], "Mx_1x1",
                                  username="u", password="p",
                                  on_error="raise")


# ---------------------------------------------------------------------------
# HFD multi
# ---------------------------------------------------------------------------


@resp_lib.activate
def test_read_hfd_web_multi_two_countries():
    resp_lib.add(resp_lib.GET, HFD_LOGIN_URL, body=_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, HFD_LOGIN_URL, body="", status=200)
    _register_hfd_country("USA")
    _register_hfd_country("SWE")

    df = pyhmfd.read_hfd_web_multi(["USA", "SWE"], "asfrRR",
                                   username="u", password="p")

    assert "country" in df.columns
    assert set(df["country"].unique()) == {"USA", "SWE"}
    assert "OpenInterval" in df.columns
