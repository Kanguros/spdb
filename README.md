# SPDB

Implement your own _relational database_ on SharePoint Lists! No infrastructure, no database server, no maintenance overhead.

## Use Cases

- Store and query structured data without installing or maintaining a database server.
- Bypass the need for formal datbase deployment procedures in large organizations — use existing SharePoint infrastructure.
- Leverage SharePoint’s built-in GUI for data entry, filtering, and customization.

## Limitations

- Maximum 5,000 items per SharePoint list (SharePoint Online default limit).
- Model definitions in code are not enforced at the SharePoint list level

## How It Works

- Define your data structure using Pydantic models.
- Authenticate and connect to your SharePoint site.
- Interact with your lists as if they were database tables, with support for lazy loading and relationship expansion.

## Using SPDB in Your Project

### 1. Define Your Models

```python
from pydantic import BaseModel, Field

class Role(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    description: str | None = Field(None, alias="Description")

class Application(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    version: str | None = Field(None, alias="Version")
    language: str | None = Field(None, alias="Language")
    is_active: bool = Field(True, alias="Is Active")

class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    ip_address: str | None = Field(None, alias="Ip Address")
    operating_system: str | None = Field(None, alias="Operating System")
    application: str = Field(..., alias="Application")  # Lazy: just the name
    roles: list[str] = Field(default_factory=list, alias="Roles")  # Lazy: just the names
    location: str | None = Field(None, alias="Location")
    is_virtual: bool = Field(False, alias="Is Virtual")
```

### 2. Implement Your SPDB Class

```python
from my_spdb.models import Application, Role, Server
from spdb.base import SPDB
from spdb.provider import SharePointProvider

class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    models = [Server, Application, Role]
    def __init__(self, username: str, password: str, verify=None):
        self.username = username
        self.password = password
        self.verify = verify
        provider = SharePointProvider(self.url, self.username, password, verify=self.verify)
        super().__init__(provider, self.models)
```

### 3. Query Data

```python
spdb = MySPDB("user", "pass")

servers = spdb.get_models(Server)
server = servers[0]

print(server.application)
# 'Application1' (lazy, as a string)
```

### 4. Expand Relationships

```python
servers = spdb.get_models(Server, expanded=True)
server = servers[0]

print(server.application.name)
# 'Application1'
print(server.application)
# Application model instance
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
