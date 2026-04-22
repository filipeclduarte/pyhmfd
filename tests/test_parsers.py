"""Unit tests for parsers and utils — no network access required."""

import io

import pandas as pd
import pytest

from pyhmfd.parsers import hfd_parse, hfc_parse, hmd_parse
from pyhmfd.utils import parse_age_column, read_table_from_text


# ---------------------------------------------------------------------------
# parse_age_column
# ---------------------------------------------------------------------------


def test_parse_age_open_interval():
    s = pd.Series(["0", "1", "5", "110+"])
    age, open_iv = parse_age_column(s)
    assert list(age) == [0, 1, 5, 110]
    assert list(open_iv) == [False, False, False, True]


def test_parse_age_range_suffix():
    # Trailing '-' strips cleanly but does NOT mark open interval
    s = pd.Series(["85-", "90"])
    age, open_iv = parse_age_column(s)
    assert list(age) == [85, 90]
    assert list(open_iv) == [False, False]


# ---------------------------------------------------------------------------
# read_table_from_text
# ---------------------------------------------------------------------------

_HMD_TEXT = """\
Deaths, Sweden, 1x1 (period 1x1), Last modified: 01-Jan-2024

   Age    Female   Male    Total
     0  1000.00  1100.0  2100.0
     1   200.00   220.0   420.0
  110+     1.00     2.0     3.0
"""


def test_read_table_from_text_shape():
    df = read_table_from_text(_HMD_TEXT)
    assert df.shape == (3, 4)
    assert "Age" in df.columns


def test_read_table_from_text_na():
    text = "Header line\nSecond description line\nCol1 Col2\n1 .\n2 5\n"
    df = read_table_from_text(text)
    assert pd.isna(df["Col2"].iloc[0])


# ---------------------------------------------------------------------------
# hmd_parse
# ---------------------------------------------------------------------------


def test_hmd_parse_adds_open_interval():
    df = read_table_from_text(_HMD_TEXT)
    out = hmd_parse(df)
    assert "OpenInterval" in out.columns
    assert out["OpenInterval"].iloc[-1] is True or out["OpenInterval"].iloc[-1] == True


def test_hmd_parse_age_dtype():
    df = read_table_from_text(_HMD_TEXT)
    out = hmd_parse(df)
    assert pd.api.types.is_integer_dtype(out["Age"])


# ---------------------------------------------------------------------------
# hfd_parse
# ---------------------------------------------------------------------------

_HFD_TEXT = """\
Age-specific fertility rates, USA
Last modified: 01-Jan-2024
Age   ASFR    Exposure
12    0.001   5000.0
49    0.0005  4500.0
55+   .       3000.0
"""


def test_hfd_parse_open_interval():
    df = read_table_from_text(_HFD_TEXT)
    out = hfd_parse(df, item="asfrRR")
    assert "OpenInterval" in out.columns
    assert out["OpenInterval"].iloc[-1] == True


def test_hfd_parse_asfr_dtype():
    df = read_table_from_text(_HFD_TEXT)
    out = hfd_parse(df, item="asfrRR")
    assert pd.api.types.is_float_dtype(out["ASFR"])


# ---------------------------------------------------------------------------
# hfc_parse
# ---------------------------------------------------------------------------

_HFC_TEXT = """\
Human Fertility Collection, Russia
Last modified: 01-Jan-2024
Country  Year1  Year2  AgeInterval   ASFR
RUS       1990   1991            1  0.050
RUS       1990   1991            w      .
"""


def test_hfc_parse_open_interval():
    df = read_table_from_text(_HFC_TEXT)
    out = hfc_parse(df)
    assert "OpenInterval" in out.columns
    assert out["OpenInterval"].iloc[-1] == True
    assert out["OpenInterval"].iloc[0] == False


def test_hfc_parse_year_dtype():
    df = read_table_from_text(_HFC_TEXT)
    out = hfc_parse(df)
    assert pd.api.types.is_integer_dtype(out["Year1"])
