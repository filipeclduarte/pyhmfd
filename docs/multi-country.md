# Multi-country Download

`pyhmfd` can download data for multiple countries in a single call.
A single authenticated session is shared across all requests, and downloads
run in parallel using a thread pool — significantly faster than looping.

## Basic usage

```python
import pyhmfd

# HMD — three countries at once
df = pyhmfd.read_hmd_web_multi(
    countries=["AUS", "USA", "SWE"],
    item="Mx_1x1",
)
print(df["country"].unique())  # ['AUS', 'SWE', 'USA']
print(df.shape)                # (rows for all three combined, columns)

# HFD — multiple countries
df = pyhmfd.read_hfd_web_multi(
    countries=["USA", "SWE", "JPN"],
    item="asfrRR",
)
```

## Download all countries

Pass `countries="all"` to automatically fetch the full list and download
every available country:

```python
# All HMD countries
df = pyhmfd.read_hmd_web_multi(countries="all", item="Mx_1x1")

# All HFD countries
df = pyhmfd.read_hfd_web_multi(countries="all", item="asfrRR")
```

## Controlling parallelism

The `workers` parameter controls the number of parallel download threads
(default: `4`). Increase it for faster bulk downloads:

```python
df = pyhmfd.read_hmd_web_multi(
    countries="all",
    item="Mx_1x1",
    workers=8,
)
```

!!! warning "Be considerate"
    Avoid setting `workers` too high. The HMD and HFD servers are public
    research infrastructure — excessive parallel requests may be rate-limited
    or flagged. Values between 4 and 8 are generally safe.

## Error handling

By default (`on_error="warn"`), countries that fail are skipped and a warning
is emitted. The remaining countries are still downloaded.

```python
# Default: warn and continue
df = pyhmfd.read_hmd_web_multi(
    ["AUS", "USA", "INVALID"],
    "Mx_1x1",
    on_error="warn",   # default
)
# UserWarning: Failed to download 1 country/countries:
#   INVALID: HMD INVALID/Mx_1x1 failed with HTTP 404

# Strict: raise on first error
df = pyhmfd.read_hmd_web_multi(
    ["AUS", "USA"],
    "Mx_1x1",
    on_error="raise",
)
```

## Output format

The result is a single `pandas.DataFrame` with:

- A leading `country` column containing the short code.
- All the usual columns for the requested item (`Year`, `Age`, `Female`, `Male`, `Total`, `OpenInterval`, …).
- Sorted by `country`, then `Year`, then `Age`.

```python
df = pyhmfd.read_hmd_web_multi(["AUS", "USA"], "Mx_1x1")
print(df.head())
#   country  Year  Age    Female      Male     Total  OpenInterval
# 0     AUS  1921    0  0.059987  0.076533  0.068444         False
# 1     AUS  1921    1  0.012064  0.014339  0.013225         False
# ...
```
