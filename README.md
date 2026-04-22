# pyhmfd

A Python package for reading data from the Human Mortality Database (HMD),
Human Fertility Database (HFD), Human Fertility Collection (HFC),
Japanese Mortality Database (JMD), and Canadian Historical Mortality Database (CHMD).

Returns tidy `pandas.DataFrame` objects ready for analysis.

## Credits

This package is a Python port of the R package **HMDHFDplus** by
Tim Riffe, Jose Manuel Aburto, and contributors:

> Riffe T, Aburto JM, et al. (2023). *HMDHFDplus: Read Human Mortality Database
> and Human Fertility Database Data from the Web*. R package.
> <https://github.com/timriffe/HMDHFDplus>

The authentication flow, URL patterns, parsing logic, and data-cleaning
conventions are derived directly from that work. Licensed under GPL-2.0.

## Supported databases

| Database | Short name | Authentication |
|---|---|---|
| [Human Mortality Database](https://www.mortality.org) | HMD | account required |
| [Human Fertility Database](https://www.humanfertility.org) | HFD | account required |
| [Human Fertility Collection](https://www.fertilitydata.org) | HFC | none |
| [Japanese Mortality Database](https://www.ipss.go.jp/p-toukei/JMD) | JMD | none |
| [Canadian Historical Mortality Database](https://www.prdh.umontreal.ca/BDLC) | CHMD | none |

## Installation

```bash
pip install pyhmfd
```

Or from source:

```bash
git clone https://github.com/filipeclduarte/pyhmfd.git
cd pyhmfd
pip install -e ".[dev]"
```

## Credentials

For HMD and HFD you need a free account at their respective websites.
Supply credentials via environment variables (recommended for scripts/CI):

```bash
export HMD_USER="your@email.com"
export HMD_PASSWORD="yourpassword"
export HFD_USER="your@email.com"
export HFD_PASSWORD="yourpassword"
```

Or pass them directly to the function, or let the package prompt interactively.
Credentials entered interactively are offered to the system keyring for storage.

## Quick start

### Single country

```python
import pyhmfd

# Human Mortality Database — needs credentials
df = pyhmfd.read_hmd_web("USA", "Mx_1x1")
df = pyhmfd.read_hmd_web("FRATNP", "Deaths_1x1", username="u@example.com", password="pw")

# Human Fertility Database — needs credentials
df = pyhmfd.read_hfd_web("USA", "asfrRR")

# Japanese Mortality Database — no auth
df = pyhmfd.read_jmd_web("01", "Deaths_1x1")   # 01 = Hokkaido

# Canadian Historical Mortality Database — no auth
df = pyhmfd.read_chmd_web("que", "Mx_1x1")     # que = Quebec

# Human Fertility Collection — no auth
df = pyhmfd.read_hfc_web("RUS", "ASFRstand")

# Read a locally downloaded file
df = pyhmfd.read_hmd("/path/to/Mx_1x1.txt")
df = pyhmfd.read_hfd("/path/to/asfrRR.txt", item="asfrRR")
```

### Multiple countries

Download data for several countries in a single call. A shared authenticated
session is reused across all downloads and requests run in parallel.

```python
import pyhmfd

# HMD — download Mx_1x1 for three countries at once
df = pyhmfd.read_hmd_web_multi(
    countries=["AUS", "USA", "SWE"],
    item="Mx_1x1",
    workers=4,          # parallel download threads (default: 4)
)
print(df["country"].unique())   # ['AUS', 'SWE', 'USA']
print(df.head())
#   country  Year  Age    Female      Male     Total  OpenInterval
# 0     AUS  1921    0  0.059987  0.076533  0.068444         False
# ...

# HFD — download asfrRR for multiple countries
df = pyhmfd.read_hfd_web_multi(
    countries=["USA", "SWE", "JPN"],
    item="asfrRR",
    workers=4,
)

# Download all available countries
df = pyhmfd.read_hmd_web_multi(countries="all", item="Mx_1x1", workers=8)
df = pyhmfd.read_hfd_web_multi(countries="all", item="asfrRR", workers=8)
```

#### Error handling

By default, a country that fails (e.g. item not available) emits a warning and
is skipped so the rest of the download completes. Use `on_error="raise"` to
stop immediately on the first failure.

```python
# Warn and skip failing countries (default)
df = pyhmfd.read_hmd_web_multi(
    ["AUS", "USA", "XXX"],
    "Mx_1x1",
    on_error="warn",
)

# Raise immediately on first error
df = pyhmfd.read_hmd_web_multi(
    ["AUS", "USA"],
    "Mx_1x1",
    on_error="raise",
)
```

## Utility functions

```python
# List available countries
pyhmfd.get_hmd_countries()         # ['AUS', 'AUT', ..., 'USA']
pyhmfd.get_hfd_countries()         # DataFrame with country names and codes
pyhmfd.get_hfc_countries()         # list of codes
pyhmfd.get_jmd_prefectures()       # dict: name → 2-digit code
pyhmfd.get_chmd_provinces()        # ['alb', 'bco', 'can', ...]

# List available data items per country
pyhmfd.get_hmd_items("USA")        # DataFrame: item, description, url
pyhmfd.get_hfd_items("USA")        # DataFrame: item, description, url

# Last-update date for an HFD country
pyhmfd.get_hfd_date("USA")         # '20260323' (date of last update)
```

## Output format

All functions return a `pandas.DataFrame`. When `fixup=True` (default):

- `Age` column is `Int64` (nullable integer).
- `OpenInterval` boolean column marks the terminal open age group (e.g. 110+).
- `Year` and `Cohort` are `Int64`.
- Rate and count columns are `float64`.
- Missing values coded as `'.'` in source files become `NaN`.

Multi-country functions add a leading `country` column with the country short
code, and the result is sorted by `country`, `Year`, `Age`.

## API reference

| Function | Database | Auth |
|---|---|---|
| `read_hmd_web(country, item)` | HMD | yes |
| `read_hmd_web_multi(countries, item)` | HMD | yes |
| `read_hmd(filepath)` | local file | — |
| `read_hfd_web(country, item)` | HFD | yes |
| `read_hfd_web_multi(countries, item)` | HFD | yes |
| `read_hfd(filepath)` | local file | — |
| `read_jmd_web(pref_id, item)` | JMD | no |
| `read_chmd_web(prov_id, item)` | CHMD | no |
| `read_hfc_web(country, item)` | HFC | no |
| `get_hmd_countries()` | HMD | no |
| `get_hmd_items(country)` | HMD | no |
| `get_hfd_countries()` | HFD | no |
| `get_hfd_items(country)` | HFD | no |
| `get_hfd_date(country)` | HFD | no |
| `get_hfc_countries()` | HFC | no |
| `get_jmd_prefectures()` | JMD | — |
| `get_chmd_provinces()` | CHMD | — |

## Running tests

```bash
pytest
```

## License

GPL-2.0, following the original R package.
