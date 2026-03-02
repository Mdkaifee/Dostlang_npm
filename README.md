# worklib

A Python package to build and run your own DostLang-style mini programming language.

## Install (after publishing)

```bash
pip install worklib
```

## Install via npm (global CLI)

```bash
npm i -g dostlang
```

Then run:

```bash
dostlang -c $'yeh_ha x = 5\ndost_bol x * 2'
```

Note: npm CLI requires Python 3 installed on your system.

## Language quick start

Create `hello.dost`:

```txt
yeh_ha name = "apni bhasha"
dost_bol "Welcome to " + name

yeh_ha x = 1
jabtak x <= 3 {
  dost_bol x
  x = x + 1
}
```

Run with CLI:

```bash
dostlang hello.dost
```

Or run inline:

```bash
dostlang -c $'yeh_ha x = 5\ndost_bol x * 2'
```

## Python API

```python
from worklib import run_source

code = """
yeh_ha a = 10
agar a > 5 {
  dost_bol "A bada hai"
} warna {
  dost_bol "A chota hai"
}
"""

result = run_source(code)
print(result.output)      # ['A bada hai']
print(result.variables)   # {'a': 10}
```

## Language syntax (v0.1)

- `yeh_ha x = expr`: declare a variable
- `x = expr`: update variable
- `dost_bol expr`: print output
- `agar condition { ... } warna { ... }`: conditional
- `jabtak condition { ... }`: loop
- Booleans: `sach`, `jhoot`
- Logic: `aur`, `ya`, `nahi`

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Publish to PyPI

1. Update metadata in `pyproject.toml` (`name`, `authors`, `urls`).
2. Bump `version` in `pyproject.toml`.
3. Build distributions:
   ```bash
   python -m build
   ```
4. Upload to TestPyPI first:
   ```bash
   twine upload --repository testpypi dist/*
   ```
5. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

Use an API token for secure upload:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-<your-token>
```
# Dostlang_npm
