This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.
The content has been processed where empty lines have been removed.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching these patterns are excluded: **/__init__.py, tests/**, .gitignore, .pre-commit-config.yaml, poetry.lock, pyproject.toml, repomix.config.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Empty lines have been removed from all files
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
my_spdb/core.py
my_spdb/models.py
my_spdb/tests/test_my_spdb.py
README.md
spdb/base.py
spdb/model.py
spdb/provider.py
```

# Files

## File: my_spdb/tests/test_my_spdb.py
```python
# ruff: noqa: S101
import pytest
from my_spdb.core import MySPDB
from my_spdb.models import Application, Role, Server
@pytest.fixture(scope="module")
def myspdb():
    return MySPDB("username1", "password")
def test_myspdb_models(myspdb):
    assert myspdb.models == [Server, Application, Role]
@pytest.mark.parametrize("name", [Server, Application, Role])
def test_get_models(name: str, myspdb):
    items = myspdb.get_models(name=name, expanded=True)
    assert items and len(items) > 10
def test_get_server_models_expanded(myspdb):
    servers = myspdb.get_models(name=Server, expanded=True)
    for server in servers:
        if server.application:
            assert isinstance(server.application, Application)
        if server.roles:
            assert all(isinstance(role, Role) for role in server.roles)
```

## File: spdb/model.py
```python
from pydantic import BaseModel as PydanticBaseModel
class BaseModel(PydanticBaseModel):
    pass
```

## File: my_spdb/core.py
```python
from my_spdb.models import Application, Role, Server
from spdb.base import SPDB
from spdb.provider import SharePointProvider
class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    """With lists under the same name as model"""
    models = [Server, Application, Role]
    def __init__(self, username: str, password: str, verify=None):
        self.username = username
        self.password = password
        self.verify = verify
        super().__init__(SharePointProvider(self.url, self.username, password, verify=self.verify), self.models)
```

## File: my_spdb/models.py
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
    application: Application = Field(..., alias="Application")
    roles: list[Role] = Field(default_factory=list, alias="Roles")
    location: str | None = Field(None, alias="Location")
    is_virtual: bool = Field(False, alias="Is Virtual")
```

## File: README.md
```markdown
# SPDB

Implement your own _relational database_ on SharePoint Lists!
```

## File: spdb/base.py
```python
from typing import Any, TypeVar
from pydantic import BaseModel
from .provider import SharePointProvider
T = TypeVar("T", bound=BaseModel)
class SPDB:
    """
    SPDB allows reading SharePoint lists as Pydantic models, supporting both lazy and full expansion of related
    fields. Related fields are detected automatically via Pydantic model annotations.
    Example usage:
        spdb = SPDB(provider, models=[Device, Application])
        devices = spdb.get_models(Device)                 # Lazy: related fields remain identifiers
        devices_full = spdb.get_models(Device, expanded=True)  # Full: related fields are hydrated models
    """
    def __init__(
        self,
        provider: SharePointProvider,
        models: list[type[BaseModel]],
    ):
        self.provider = provider
        self._models: dict[str, type[BaseModel]] = {m.__name__: m for m in models}
        self._cache: dict[str, list[BaseModel]] = {}
    def get(
        self,
        model_cls: type[T],
        full: bool = False,
    ) -> list[T]:
        """
        Retrieve list of models of type `model_cls`.
        Args:
            model_cls: The Pydantic model class to load.
            full: If True, expand and hydrate all related fields.
        Returns:
            list of Pydantic model instances.
        """
        name = model_cls.__name__
        if name not in self._cache:
            self._cache[name] = self._load(model_cls)
        items: list[T] = self._cache[name]  # type: ignore
        return self._expand(items) if full else items
    def get_models(
        self,
        name: type[T],
        expanded: bool = False,
    ) -> list[T]:
        """
        Alias for get().
        Args:
            name: The model class.
            expanded: If True, fully expand relations.
        """
        return self.get(name, full=expanded)
    def _load(self, model_cls: type[T]) -> list[T]:
        """Load raw data from SharePoint into Pydantic models without expanding relations."""
        raw = self.provider.get_data(model_cls.__name__)
        return [model_cls(**item) for item in raw]
    def _expand(self, items: list[T]) -> list[T]:
        """Fully expand related model fields based on identifier lookups."""
        # Build lookup maps per model by name or id
        lookups: dict[str, dict[Any, BaseModel]] = {}
        for model_name, cls in self._models.items():
            if model_name not in self._cache:
                self._cache[model_name] = self._load(cls)
            index = {getattr(obj, 'name', getattr(obj, 'id')): obj for obj in self._cache[model_name]}
            lookups[model_name] = index
        expanded: list[T] = []
        for obj in items:
            updates: dict[str, Any] = {}
            data = obj.model_dump()
            for field_name, field_info in obj.model_fields.items():
                rel_name = field_info.annotation.__name__ if isinstance(field_info.annotation, type) else None
                if rel_name and rel_name in lookups:
                    key = data.get(field_name)
                    if key in lookups[rel_name]:
                        updates[field_name] = lookups[rel_name][key]
            expanded.append(obj.copy(update=updates) if updates else obj)
        return expanded
```

## File: spdb/provider.py
```python
import logging
from typing import Any
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml import CamlQuery
from office365.sharepoint.lists.list import List as SPlist
class SharePointProvider:
    def __init__(
        self,
        site_url: str,
        username: str,
        password: str,
        verify: str | None = None,
    ):
        """
        Initializes the SharePointProvider with authentication details and site URL.
        Args:
            site_url (str): The URL of the SharePoint site.
            username (str): Username for SharePoint authentication.
            password (str): Password for SharePoint authentication.
            verify (str | None): Path to SSL certificate for verification, or None to disable verification.
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        self.verify = verify
        self.ctx = None
        self._authenticated = False
        self._cache = {}
        if not self.username or not self.password:
            raise ValueError("Username and password must be provided")
        logging.debug(
            f"SharePointProvider initialized for site '{self.site_url}' with user '{self.username}'."
        )
    @property
    def client_context(self) -> ClientContext:
        """
        Returns the authenticated SharePoint client context.
        Returns:
            ClientContext: Authenticated SharePoint client context.
        """
        if not self.ctx or not self._authenticated:
            logging.debug("Authenticating SharePoint client context.")
            self._authenticate()
            self._authenticated = True
        return self.ctx
    def _authenticate(self):
        """
        Authenticates with SharePoint using the provided credentials.
        Raises:
            Exception: If authentication fails.
        """
        try:
            logging.debug(
                f"Attempting authentication for user '{self.username}' at '{self.site_url}'"
            )
            ctx_auth = AuthenticationContext(self.site_url)
            if ctx_auth.acquire_token_for_user(self.username, self.password):
                self.ctx = ClientContext(self.site_url, ctx_auth)
                logging.info("SharePoint authentication successful.")
            else:
                error_msg = ctx_auth.get_last_error()
                logging.error(f"SharePoint authentication failed: {error_msg}")
                raise Exception(f"Authentication failed: {error_msg}")
        except Exception as e:
            logging.error(f"SharePoint authentication error: {str(e)}")
            raise
    def get_list(self, list_name: str) -> SPlist:
        """
        Retrieves a SharePoint list by its name.
        Args:
            list_name (str): The name of the SharePoint list.
        Returns:
            SPlist: The SharePoint list object.
        """
        logging.debug(f"Fetching SharePoint list: '{list_name}'")
        return self.client_context.web.lists.get_by_title(list_name)
    def get_list_items(self, list_name: str) -> list[dict[str, Any]]:
        """
        Fetch all items from a SharePoint list. Uses in-memory cache if data was already retrieved.
        Args:
            list_name: The title of the SharePoint list.
        Returns:
            A list of dictionaries representing SharePoint list items.
        """
        if list_name in self._cache:
            return self._cache[list_name]
        sp_list = self.get_list(list_name)
        items = sp_list.get_items(CamlQuery())
        self.ctx.load(items)
        self.ctx.execute_query()
        parsed_items = [item.properties for item in items]
        self._cache[list_name] = parsed_items
        return parsed_items
    def clear_cache(self, list_name: str | None = None) -> None:
        """
        Clears the internal cache.
        Args:
            list_name (Optional[str]): If provided, only clears the cache for the given list.
                                       If None, clears the entire cache.
        """
        if list_name:
            self._cache.pop(list_name, None)
        else:
            self._cache.clear()
```
