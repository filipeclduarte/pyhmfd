# Getting Started

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

The HMD and HFD require a free account. Register at:

- HMD: [mortality.org](https://www.mortality.org/Account/Register)
- HFD: [humanfertility.org](https://www.humanfertility.org/Account/Register)

### Setting credentials

**Environment variables (recommended for scripts and CI):**

```bash
export HMD_USER="your@email.com"
export HMD_PASSWORD="yourpassword"
export HFD_USER="your@email.com"
export HFD_PASSWORD="yourpassword"
```

**Pass directly to the function:**

```python
df = pyhmfd.read_hmd_web("AUS", "Mx_1x1", username="your@email.com", password="yourpassword")
```

**Interactive prompt:**

If no credentials are found, the package prompts for them in the terminal.
Credentials entered interactively are stored in the system keyring so you
won't be asked again.

!!! tip
    For automated workflows (CI/CD, notebooks), always use environment
    variables to avoid interactive prompts.
