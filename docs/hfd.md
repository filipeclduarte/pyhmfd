# Human Fertility Database (HFD)

The [Human Fertility Database](https://www.humanfertility.org) provides
age-specific fertility rates and related indicators for about 40 countries.
An account is required.

## Reading data from the web

```python
import pyhmfd

# Age-specific fertility rates, period (rectangles)
df = pyhmfd.read_hfd_web("USA", "asfrRR")

# Mean age at birth
df = pyhmfd.read_hfd_web("SWE", "mabRR")

# Total fertility rate
df = pyhmfd.read_hfd_web("JPN", "tfrRR")
```

## Reading a local file

```python
df = pyhmfd.read_hfd("/path/to/asfrRR.txt", item="asfrRR")
```

## Listing countries and items

```python
# All available countries
countries = pyhmfd.get_hfd_countries()
print(countries)
#       country  code
# 0      Austria   AUT
# 1      Belarus   BLR
# ...

# Items available for a specific country
items = pyhmfd.get_hfd_items("USA")
print(items)

# Date of last update for a country
print(pyhmfd.get_hfd_date("USA"))  # '20260323'
```

## Common data items

| Item | Description |
|---|---|
| `asfrRR` | Age-specific fertility rates, period (rectangles) |
| `asfrTR` | Age-specific fertility rates, period (triangles) |
| `asfrVH` | Age-specific fertility rates, cohort |
| `tfrRR` | Total fertility rate, period |
| `mabRR` | Mean age at birth, period |
| `birthsRR` | Live births, period |
| `exposRR` | Female population exposure, period |

!!! note "Country availability"
    Australia is **not** in the HFD. Use `get_hfd_countries()` to see the
    full list of available countries.
