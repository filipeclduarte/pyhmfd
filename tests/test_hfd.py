"""Tests for HFD reader using mocked HTTP responses."""

import responses as resp_lib
import pytest

import pyhmd
from pyhmd.hfd import _BASE, _LOGIN_URL

_MOCK_DATA = """\
Age-specific fertility rates, USA, period
Last modified: 01-Jan-2024
Age    ASFR   Exposure
12    0.0010   5000.0
49    0.0005   4500.0
55+        .   3000.0
"""

_MOCK_LOGIN_HTML = """\
<html><form>
<input name="__RequestVerificationToken" value="tok456"/>
</form></html>
"""

_MOCK_COUNTRY_PAGE = """\
<html><body>
<a href="/Files/USA/20240101/USAasfrRR.txt">ASFR RR</a>
</body></html>
"""


@resp_lib.activate
def test_read_hfd_web_success():
    resp_lib.add(resp_lib.GET, f"{_BASE}/Country/GetData/USA",
                 body=_MOCK_COUNTRY_PAGE, status=200, content_type="text/html")
    resp_lib.add(resp_lib.GET, _LOGIN_URL, body=_MOCK_LOGIN_HTML, status=200,
                 content_type="text/html")
    resp_lib.add(resp_lib.POST, _LOGIN_URL, body="", status=200)
    resp_lib.add(
        resp_lib.GET,
        f"{_BASE}/File/GetDocument/Files/USA/20240101/USAasfrRR.txt",
        body=_MOCK_DATA,
        status=200,
        content_type="text/plain",
    )

    df = pyhmd.read_hfd_web("USA", "asfrRR", username="u", password="p")
    assert not df.empty
    assert "OpenInterval" in df.columns
    assert df["ASFR"].iloc[0] == pytest.approx(0.0010)


@resp_lib.activate
def test_get_hfd_date():
    resp_lib.add(resp_lib.GET, f"{_BASE}/Country/GetData/USA",
                 body=_MOCK_COUNTRY_PAGE, status=200, content_type="text/html")
    date = pyhmd.get_hfd_date("USA")
    assert date == "20240101"
