# SPDB: SharePoint as a Relational Database

Implement your own _relational database_ on SharePoint Lists! No infrastructure, no database server, no maintenance overhead.

---

## Features

- Store and query structured data using SharePoint as a backend
- Define models with Pydantic and Python type hints
- Lazy loading and automatic expansion of relationships
- No database server or extra infrastructure required
- Leverage SharePoint’s built-in GUI for data entry and filtering

---

## Installation

Install with [Poetry](https://python-poetry.org/):

```sh
poetry add spdb
```

Or with pip:

```sh
pip install spdb
```

**Requirements:**

- Python 3.10+
- SharePoint access (username/password)

---

## Quickstart

### 1. Define Your Models

Use `Annotated` and `Field` for all model attributes. Use `LookupField` for fields that represent relationships (foreign keys).

```python file=spdb_example\models.py
from typing import Annotated

from pydantic import Field

from spdb.model import BaseModel, LookupField


class Role(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    description: Annotated[str, Field("", alias="Description")]


class Team(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    members: Annotated[list[str], Field(default_factory=list, alias="Members")]


class Application(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    version: Annotated[str | None, Field(default=None, alias="Version")]
    language: Annotated[str | None, Field(default=None, alias="Language")]
    is_active: Annotated[bool, Field(default=True, alias="Is Active")]
    owner: Annotated[
        str | Team, LookupField, Field(default=None, alias="Owner")
    ]


class Server(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    hostname: Annotated[str, Field(..., alias="Hostname")]
    application: Annotated[
        Application | str, Field(..., alias="Application"), LookupField
    ]
    ip_address: Annotated[str | None, Field(default=None, alias="Ip Address")]
    operating_system: Annotated[
        str | None, Field(None, alias="Operating System")
    ]
    roles: Annotated[
        list[str] | list[Role],
        Field(default_factory=list, alias="Roles"),
        LookupField,
    ]
    location: Annotated[str | None, Field(default=None, alias="Location")]
    is_virtual: Annotated[bool, Field(default=False, alias="Is Virtual")]
```

### 2. Create Your SPDB Class

```python
from spdb.base import SPDB
from spdb.provider import SharePointProvider

class MySPDB(SPDB):
    url = "https://your_sharepoint_site/"
    models = [Server, Application, Role]
    def __init__(self, username: str, password: str, verify=None):
        provider = SharePointProvider(self.url, username, password, verify=verify)
        super().__init__(provider, self.models)
```

### 3. Query Data

```python
spdb = MySPDB("user", "pass")
servers = spdb.get_models(Server)
print(servers[0].application)  # 'Application1' (lazy, as a string)
```

---

## Usage

- **Lazy loading**: By default, related fields are returned as strings (e.g., application name).
- **Relationship expansion**: Use `expanded=True` to hydrate related fields as model instances.

```python
# Lazy (default)
servers = spdb.get_models(Server)
print(servers[0].application)  # 'Application1'

# Expanded
servers = spdb.get_models(Server, expanded=True)
print(servers[0].application.name)  # 'Application1'
print(isinstance(servers[0].application, Application))  # True
```

---

## Relationship Expansion

- Fields with `LookupField` and a model type are automatically expanded.
- Lists of related models are supported.

---

## Testing

- Tests use mock SharePoint data for reliability.
- Run tests with:

```sh
pytest
```

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
