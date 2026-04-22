# Other Databases

## Japanese Mortality Database (JMD)

The [JMD](https://www.ipss.go.jp/p-toukei/JMD) provides mortality data for
Japan's 47 prefectures. No authentication required.

```python
import pyhmfd

# All Japan (code "00")
df = pyhmfd.read_jmd_web("00", "Mx_1x1")

# Hokkaido (code "01")
df = pyhmfd.read_jmd_web("01", "Deaths_1x1")

# List all prefecture codes
prefectures = pyhmfd.get_jmd_prefectures()
print(prefectures)
# {'All Japan': '00', 'Hokkaido': '01', 'Aomori': '02', ...}
```

## Canadian Historical Mortality Database (CHMD)

The [CHMD](https://www.prdh.umontreal.ca/BDLC) provides mortality data for
Canadian provinces and territories. No authentication required.

```python
# All Canada
df = pyhmfd.read_chmd_web("can", "Mx_1x1")

# Quebec
df = pyhmfd.read_chmd_web("que", "Mx_1x1")

# List all province codes
provinces = pyhmfd.get_chmd_provinces()
print(provinces)
# ['alb', 'bco', 'can', 'man', 'nbr', 'nfl', 'nsc', 'nwt', 'ont', 'pei', 'que', 'sas', 'yuk']
```

### CHMD province codes

| Province / Territory | Code |
|---|---|
| Canada (all) | `can` |
| Alberta | `alb` |
| British Columbia | `bco` |
| Manitoba | `man` |
| New Brunswick | `nbr` |
| Newfoundland | `nfl` |
| Nova Scotia | `nsc` |
| Northwest Territories | `nwt` |
| Ontario | `ont` |
| PEI | `pei` |
| Quebec | `que` |
| Saskatchewan | `sas` |
| Yukon | `yuk` |

## Human Fertility Collection (HFC)

The [HFC](https://www.fertilitydata.org) collects fertility data from
national statistical offices for a wide range of countries and sub-populations.
No authentication required.

```python
# Russia, age-standardised ASFR
df = pyhmfd.read_hfc_web("RUS", "ASFRstand")

# List available country codes
codes = pyhmfd.get_hfc_countries()
print(codes)  # ['ARM', 'AZE', 'BLR', ...]

# Include full country names
df_countries = pyhmfd.get_hfc_countries(names=True)
print(df_countries.head())
```
