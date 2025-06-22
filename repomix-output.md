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
- Files matching these patterns are excluded: **/**init**.py, tests/**, .gitignore, .pre-commit-config.yaml, poetry.lock, pyproject.toml, repomix.config.json, tests/\*_/_.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Empty lines have been removed from all files
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure

```
my_spdb/core.py
my_spdb/models.py
README.md
spdb/base.py
spdb/mocks.py
spdb/model.py
spdb/provider.py
```

# Files

## File: spdb/mocks.py

```python
import json
import logging
from pathlib import Path
from typing import Any
from spdb.provider import SharePointProvider
class MockSharePointProvider(SharePointProvider):
    def __init__(self, mock_data_dir: str):
        self.mock_data_dir = Path(mock_data_dir)
        self._cache: dict[str, list[dict[str, Any]]] = {}
        logging.debug(
            f"Initialized MockSharePointProvider with data from {self.mock_data_dir}"
        )
    def fetch_list_items(
        self,
        list_name: str,
        select: list[str] | None = None,
        expand: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Load mock data from a JSON file instead of querying SharePoint.
        The JSON file must be named <list_name>.json and contain a list of items.
        """
        file_path = self.mock_data_dir / f"{list_name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Mock data file not found: {file_path}")
        logging.debug(
            f"Loading mock data for list '{list_name}' from {file_path}"
        )
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise TypeError(f"Mock data in {file_path} must be a list of dicts")
        return data
```

## File: README.md

```markdown
# SPDB

Implement your own _relational database_ on SharePoint Lists!
```

## File: spdb/model.py

```python
from typing import Any, get_args, get_origin
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
class BaseModel(PydanticBaseModel):
    """Base Model"""
    model_config = ConfigDict(
        use_enum_values=True,
        validate_by_name=True,
        validate_by_alias=True,
        use_attribute_docstrings=True,
        str_strip_whitespace=True,
    )
    @classmethod
    def get_relation_fields(cls) -> dict[str, str]:
        """
        Return a mapping of field name to related class name for expandable fields.
        Supports both single and list of BaseModel relations.
        """
        relations = {}
        for field_name, field_info in cls.model_fields.items():
            model_cls = cls._extract_model_class(field_info.annotation)
            if model_cls:
                relations[field_name] = model_cls.__name__
        return relations
    @staticmethod
    def _extract_model_class(
        field_annotation: Any,
    ) -> type[PydanticBaseModel] | None:
        """Extract related model class from annotation, including handling for list[BaseModel]."""
        origin = get_origin(field_annotation)
        if origin is list:
            args = get_args(field_annotation)
            if (
                args
                and isinstance(args[0], type)
                and issubclass(args[0], PydanticBaseModel)
            ):
                return args[0]
        elif isinstance(field_annotation, type) and issubclass(
            field_annotation, PydanticBaseModel
        ):
            return field_annotation
        return None
```

## File: my_spdb/core.py

```python
from my_spdb.models import Application, Role, Server, Team
from spdb.base import SPDB
from spdb.provider import SharePointProvider
class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    """With lists under the same name as model"""
    models = [Server, Application, Role, Team]
    def __init__(self, username: str, password: str, verify=None):
        self.username = username
        self.password = password
        self.verify = verify
        super().__init__(
            SharePointProvider(
                self.url, self.username, password, verify=self.verify
            ),
            self.models,
        )
```

## File: my_spdb/models.py

```python
from pydantic import BaseModel, Field
class Role(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    description: str | None = Field(None, alias="Description")
class Team(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    members: list[str] = Field(default_factory=list, alias="Members")
class Application(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    version: str | None = Field(default=None, alias="Version")
    language: str | None = Field(default=None, alias="Language")
    is_active: bool = Field(default=True, alias="Is Active")
    owner: Team | str | None = Field(default=None, alias="Owner")
class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    ip_address: str | None = Field(default=None, alias="Ip Address")
    operating_system: str | None = Field(None, alias="Operating System")
    application: Application | str = Field(..., alias="Application")
    roles: list[Role] | list[str] = Field(default_factory=list, alias="Roles")
    location: str | None = Field(default=None, alias="Location")
    is_virtual: bool = Field(default=False, alias="Is Virtual")
```

## File: spdb/base.py

```python
from typing import Any, TypeVar
from spdb.model import BaseModel
from spdb.provider import SharePointProvider
T = TypeVar("T", bound=BaseModel)
class SPDB:
    """
    SPDB allows reading SharePoint lists as Pydantic models, supporting both lazy and full expansion of related
    fields. Related fields are detected automatically via Pydantic model annotations.
    Example usage:
        spdb = SPDB(provider, models=[Device, Application])
        devices = spdb.get_models(Device)                      # Lazy: related fields remain identifiers
        devices_full = spdb.get_models(Device, expanded=True)  # Full: related fields are hydrated models
    """
    default_provider: type[SharePointProvider] = SharePointProvider
    def __init__(
        self,
        provider: SharePointProvider,
        models: list[type[BaseModel]],
    ):
        self.provider = provider
        self._models: dict[str, type[BaseModel]] = {
            m.__name__: m for m in models
        }
        self._cache: dict[str, list[BaseModel]] = {}
        self._lookups: dict[str, dict[Any, BaseModel]] = {}
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
        return self._expand(items, model_cls) if full else items
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
        raw = self.provider.get_list_items(model_cls.__name__)
        return [model_cls(**item) for item in raw]
    def _ensure_lookups(self):
        for model_name, model_cls in self._models.items():
            if model_name not in self._cache:
                self._cache[model_name] = self._load(model_cls)
            if model_name not in self._lookups:
                self._lookups[model_name] = {
                    getattr(obj, "name", obj.id): obj
                    for obj in self._cache[model_name]
                }
    def _expand(self, items: list[T], model_cls: type[T]) -> list[T]:
        """Fully expand related model fields based on identifier lookups."""
        self._ensure_lookups()
        relations = model_cls.get_relation_fields()
        expanded: list[T] = []
        for obj in items:
            updates: dict[str, Any] = {}
            data = obj.__dict__
            for field_name, rel_model_name in relations.items():
                key = data.get(field_name)
                lookup = self._lookups.get(rel_model_name, {})
                if key in lookup:
                    updates[field_name] = lookup[key]
            expanded.append(obj.model_copy(update=updates) if updates else obj)
        return expanded
```

## File: spdb/provider.py

```python
import logging
from typing import Any
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List as SPlist
class ProviderError(ValueError):
    pass
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
        self._ctx = None
        self._authenticated = False
        self._cache = {}
        if not self.username or not self.password:
            raise ValueError("Username and password must be provided")
        logging.debug(
            f"SharePointProvider initialized for site '{self.site_url}' with user '{self.username}'."
        )
    @property
    def ctx(self) -> ClientContext:
        """
        Returns the authenticated SharePoint client context.
        Returns:
            ClientContext: Authenticated SharePoint client context.
        """
        if not self._ctx or not self._authenticated:
            logging.debug(
                f"Attempting authentication for user '{self.username}' at '{self.site_url}'"
            )
            self._ctx = self._authenticate()
            logging.info("SharePoint authentication successful.")
            self._authenticated = True
        return self._ctx
    def _authenticate(self) -> ClientContext:
        """
        Authenticates with SharePoint using the provided credentials.
        Raises:
            ProviderError: If authentication fails.
        """
        try:
            ctx_auth = AuthenticationContext(self.site_url, allow_ntlm=True)
            if ctx_auth.with_credentials(self.username, self.password):
                return ClientContext(self.site_url, ctx_auth)
            error_msg = ctx_auth.get_last_error()
            raise ProviderError(f"Authentication failed: {error_msg}")
        except Exception as e:
            logging.error(f"SharePoint authentication error: {str(e)}")
            raise
    def fetch_list(self, list_name: str) -> SPlist:
        """
        Fetches a SharePoint list by its name.
        Args:
            list_name: The name of the SharePoint list.
        Returns:
            The SharePoint list object.
        """
        logging.debug(f"Fetching SharePoint list: '{list_name}'")
        return self.ctx.web.lists.get_by_title(list_name)
    def fetch_list_items(
        self,
        list_name: str,
        select: list[str] | None = None,
        expand: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch all items from a SharePoint list.
        Args:
            list_name: The title of the SharePoint list.
        Returns:
            A list of dictionaries representing SharePoint list items.
        """
        sp_list = self.fetch_list(list_name)
        select_arg = ["*"] if select is None else select
        logging.debug(f"Fetching '{sp_list}' items with {select=} {expand=}")
        items = sp_list.get().select(select_arg).expand(expand).execute_query()
        return [item.properties for item in items]
    def get_list_items(
        self,
        list_name: str,
    ) -> list[dict[str, Any]]:
        """
        Get all items from a SharePoint list. Uses in-memory cache if data was already retrieved.
        Args:
            list_name: The title of the SharePoint list.
        Returns:
            A list of dictionaries representing SharePoint list items.
        """
        if list_name in self._cache:
            return self._cache[list_name]
        items = self.fetch_list_items(list_name)
        self._cache[list_name] = items
        return items
    def clear_cache(self, list_name: str | None = None) -> None:
        """
        Clears the internal cache.
        Args:
            list_name: If provided, only clears the cache for the given list.
                        If None, clears the entire cache.
        """
        if list_name:
            self._cache.pop(list_name, None)
        else:
            self._cache.clear()
```
