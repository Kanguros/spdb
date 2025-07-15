# Getting Started

**Learn how to define models and query SharePoint data with SPDB.**

## 1. Define Your Models

- Use `Annotated` and `Field` for all model attributes
- Use `LookupField` for relationships (foreign keys)

```python
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

## 2. Create Your SPDB Class

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

## 3. Query Data

```python
spdb = MySPDB("user", "pass")
servers = spdb.get_models(Server)
print(servers[0].application)  # 'Application1' (lazy, as a string)
```

## Relationship Expansion

- Fields with `LookupField` and a model type are automatically expanded
- Lists of related models are supported

```python
# Lazy (default)
servers = spdb.get_models(Server)
print(servers[0].application)  # 'Application1'

# Expanded
servers = spdb.get_models(Server, expanded=True)
print(servers[0].application.name)  # 'Application1'
print(isinstance(servers[0].application, Application))  # True
```

## Building Documentation with Pre-Commit

To ensure your documentation is always up-to-date, you can configure a pre-commit hook to build the documentation automatically. Follow these steps:

1. Install pre-commit if you haven't already:

    ```bash
    pip install pre-commit
    ```

2. Add the following configuration to your `.pre-commit-config.yaml` file:

    ```yaml
    repos:
        - repo: local
          hooks:
              - id: build-docs
                name: Build Documentation
                entry: poetry run sphinx-build -b html docs/source docs/build/html
                language: system
                pass_filenames: false
    ```

3. Install the pre-commit hooks:

    ```bash
    pre-commit install
    ```

Now, every time you commit changes, the documentation will be built automatically. This ensures that your documentation remains consistent with the codebase.
