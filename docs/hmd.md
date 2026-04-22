# Human Mortality Database (HMD)

The [Human Mortality Database](https://www.mortality.org) provides detailed
mortality and population data for over 40 countries. An account is required.

## Reading data from the web

```python
import pyhmfd

# Death rates (age × year, 1×1)
df = pyhmfd.read_hmd_web("AUS", "Mx_1x1")

# Deaths by Lexis triangle
df = pyhmfd.read_hmd_web("USA", "Deaths_lexis")

# Life tables
df = pyhmfd.read_hmd_web("SWE", "fltper_1x1")
```

## Reading a local file

If you have already downloaded a file from the HMD website:

```python
df = pyhmfd.read_hmd("/path/to/Mx_1x1.txt")
```

## Listing countries and items

```python
# All available country codes
countries = pyhmfd.get_hmd_countries()
print(countries)  # ['AUS', 'AUT', 'BEL', ..., 'USA']

# Items available for a specific country
items = pyhmfd.get_hmd_items("AUS")
print(items)
#           item                description
# 0      Mx_1x1      Death rates (period 1x1)
# 1      Mx_1x5      Death rates (period 1x5)
# ...
```

## Common data items

| Item | Description |
|---|---|
| `Mx_1x1` | Age-specific death rates, period 1×1 |
| `Deaths_1x1` | Deaths, period 1×1 |
| `Exposures_1x1` | Population exposures, period 1×1 |
| `fltper_1x1` | Period life tables, females |
| `mltper_1x1` | Period life tables, males |
| `bltper_1x1` | Period life tables, both sexes |
| `Population` | Population counts |

!!! note "Sub-populations"
    Some countries have sub-population codes, e.g. `FRATNP` (France, total),
    `FRACNP` (France, civilian). Use `get_hmd_countries()` to see all codes.
