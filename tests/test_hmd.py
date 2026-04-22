"""Tests for HMD reader using mocked HTTP responses."""

import responses as resp_lib
import pytest

import pyhmd
from pyhmd.hmd import _BASE, _LOGIN_URL

_MOCK_DATA = """\
Deaths, USA, 1x1 (period 1x1), Last modified: 01-Jan-2024

   Age   Female    Male    Total
     0  5000.00  5500.0  10500.0
     1   500.00   550.0   1050.0
  110+     1.00     2.0      3.0
"""

_MOCK_LOGIN_HTML = """\
<html><form>
<input name="__RequestVerificationToken" value="tok123"/>
</form></html>
"""


@resp_lib.activate
def test_read_hmd_web_success():
    resp_lib.add(resp_lib.GET, _LOGIN_URL, body=_MOCK_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, _LOGIN_URL, body="", status=200)
    resp_lib.add(
        resp_lib.GET,
        f"{_BASE}/File/GetDocument/hmd.v6/USA/STATS/Deaths_1x1.txt",
        body=_MOCK_DATA,
        status=200,
        content_type="text/plain",
    )

    df = pyhmd.read_hmd_web("USA", "Deaths_1x1", username="u", password="p")
    assert not df.empty
    assert "OpenInterval" in df.columns
    assert df["Age"].iloc[-1] == 110


@resp_lib.activate
def test_read_hmd_web_bad_credentials():
    resp_lib.add(resp_lib.GET, _LOGIN_URL, body=_MOCK_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, _LOGIN_URL, body="", status=200)
    resp_lib.add(
        resp_lib.GET,
        f"{_BASE}/File/GetDocument/hmd.v6/USA/STATS/Deaths_1x1.txt",
        body="<!DOCTYPE html><html>Login required</html>",
        status=200,
        content_type="text/html",
    )

    with pytest.raises(PermissionError):
        pyhmd.read_hmd_web("USA", "Deaths_1x1", username="bad", password="creds")
