# SPDB

Implement your own _relational database_ on SharePoint Lists! No infrastructure, no database server, no maintenance overhead.

## Overview

SPDB lets you use SharePoint lists as a relational database, leveraging Pydantic models for structure and type safety. You can define models, read data, and resolve relationships—without deploying or managing a traditional database. SPDB is ideal for organizations where deploying new infrastructure is slow or restricted, and where SharePoint is already widely used.

---

## Use Cases

- **Zero-Setup Database:** Store and query structured data without installing or maintaining a database server.
- **Enterprise Compliance:** Bypass the need for formal DB deployment procedures in large organizations—use existing SharePoint infrastructure.
- **User-Friendly Interface:** Leverage SharePoint’s built-in GUI for data entry, filtering, and customization.

---

## Limitations

- **List Size:** Maximum 5,000 items per SharePoint list (SharePoint Online default limit).
- **No Schema Enforcement:** Model definitions in code are not enforced at the SharePoint list level—data integrity relies on user discipline and validation in your application.

---

## How It Works

- **Models:** Define your data structure using Pydantic models.
- **Provider:** Authenticate and connect to your SharePoint site.
- **SPDB Core:** Interact with your lists as if they were database tables, with support for lazy loading and relationship expansion.

---

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

# All three are equivalent, with proper typing.
Servers = spdb.get_models("Server")
Servers = spdb.get_models(Server)
Servers = spdb.get_servers()

server = Servers[0]
print(server.application)  # 'Application1' (lazy, as a string)
```

### 4. Expand Relationships

```python
Servers = spdb.get_servers_expanded()
server = Servers[0]
print(server.application.name)  # 'Application1'
print(server.application)       # Application model instance
```

---

## Customization

To support your own SharePoint lists:

1. **Define a Pydantic model** for each list, matching SharePoint field names via the `alias` parameter.
2. **Add your models** to the `models` list in your custom SPDB class.
3. **Use `get_models()`** or your own helper methods to fetch and expand data.

---

## Notes

- **Filtering and Custom Views:** Use SharePoint’s web interface for ad-hoc filtering and data entry.
- **Data Validation:** Enforce data consistency in your application layer using Pydantic validation.
- **Performance:** For large datasets, consider SharePoint’s 5,000-item view threshold and plan accordingly.

---

## Getting Started

- Clone this repository.
- Install Python dependencies (`pydantic`, `office365-rest-python-client`).
- Define your models and SPDB subclass.
- Enjoy a SharePoint-backed database—no servers, no hassle.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
