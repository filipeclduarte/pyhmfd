# pyhmfd

**pyhmfd** is a Python package for reading data from five major demographic databases directly into `pandas.DataFrame` objects — ready for analysis, plotting, or modelling.

## Supported databases

| Database | Short name | Authentication |
|---|---|---|
| [Human Mortality Database](https://www.mortality.org) | HMD | account required |
| [Human Fertility Database](https://www.humanfertility.org) | HFD | account required |
| [Human Fertility Collection](https://www.fertilitydata.org) | HFC | none |
| [Japanese Mortality Database](https://www.ipss.go.jp/p-toukei/JMD) | JMD | none |
| [Canadian Historical Mortality Database](https://www.prdh.umontreal.ca/BDLC) | CHMD | none |

## Quick example

```python
import pyhmfd

# Single country
df = pyhmfd.read_hmd_web("AUS", "Mx_1x1")

# Multiple countries in parallel
df = pyhmfd.read_hmd_web_multi(["AUS", "USA", "SWE"], "Mx_1x1", workers=4)
print(df["country"].unique())  # ['AUS', 'SWE', 'USA']
```

## Credits

This package is a Python port of the R package **HMDHFDplus** by
Tim Riffe, Jose Manuel Aburto, and contributors:

> Riffe T, Aburto JM, et al. (2023). *HMDHFDplus: Read Human Mortality Database
> and Human Fertility Database Data from the Web*. R package.
> <https://github.com/timriffe/HMDHFDplus>

Licensed under GPL-2.0.
