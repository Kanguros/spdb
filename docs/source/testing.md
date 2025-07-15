# Testing

**How to test SPDB and write your own tests.**

## Overview

- All tests are in the `tests/` directory
- Tests use mock SharePoint data for reliability
- No live SharePoint access required for CI

## Running Tests

Run all tests with:

```sh
pytest
```

## Test Structure

| File/Folder   | Purpose                     |
| ------------- | --------------------------- |
| `tests/`      | All test code               |
| `tests/data/` | Mock SharePoint data (JSON) |
| `conftest.py` | Pytest fixtures             |
| `test_*.py`   | Unit and integration tests  |

## Writing Tests

- Use pytest fixtures for reusable setup
- Use mock data from `tests/data/`
- Do not require live SharePoint access

## Example Test

```python
import pytest
from spdb_example.core import MySPDB
from spdb_example.models import Server

def test_server_query():
    spdb = MySPDB("user", "pass")
    servers = spdb.get_models(Server)
    assert isinstance(servers, list)
    assert servers[0].hostname
```
