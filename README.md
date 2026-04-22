# pyhmd

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
pip install pyhmd
```

Or from source:

```bash
git clone https://github.com/filiped/pyhmd.git
cd pyhmd
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

```python
import pyhmd

# Human Mortality Database — needs credentials
df = pyhmd.read_hmd_web("USA", "Mx_1x1")
df = pyhmd.read_hmd_web("FRATNP", "Deaths_1x1", username="u@example.com", password="pw")

# Human Fertility Database — needs credentials
df = pyhmd.read_hfd_web("USA", "asfrRR")

# Japanese Mortality Database — no auth
df = pyhmd.read_jmd_web("01", "Deaths_1x1")   # 01 = Hokkaido

# Canadian Historical Mortality Database — no auth
df = pyhmd.read_chmd_web("qc", "Mx_1x1")      # qc = Quebec

# Human Fertility Collection — no auth
df = pyhmd.read_hfc_web("RUS", "ASFRstand")

# Read a locally downloaded file
df = pyhmd.read_hmd("/path/to/Mx_1x1.txt")
df = pyhmd.read_hfd("/path/to/asfrRR.txt", item="asfrRR")
```

## Utility functions

```python
# List available countries
pyhmd.get_hmd_countries()         # ['AUS', 'AUT', ..., 'USA']
pyhmd.get_hfd_countries()         # DataFrame with country names and codes
pyhmd.get_hfc_countries()         # list of codes
pyhmd.get_jmd_prefectures()       # dict: name → 2-digit code
pyhmd.get_chmd_provinces()        # ['ab', 'bc', 'can', ...]

# List available data items per country
pyhmd.get_hmd_items("USA")        # DataFrame: item, description, url
pyhmd.get_hfd_items("USA")        # DataFrame: item, description, url

# Last-update date for an HFD country
pyhmd.get_hfd_date("USA")         # '20240101'
```

## Output format

All functions return a `pandas.DataFrame`. When `fixup=True` (default):

- `Age` column is `Int64` (nullable integer).
- `OpenInterval` boolean column marks the terminal open age group (e.g. 110+).
- `Year` and `Cohort` are `Int64`.
- Rate and count columns are `float64`.
- Missing values coded as `'.'` in source files become `NaN`.

## Running tests

```bash
pytest
```

## License

GPL-2.0, following the original R package.
