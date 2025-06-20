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
spdb/base.py
spdb/expander.py
spdb/model.py
spdb/provider.py
```

# Files

## File: my_spdb/core.py
```python
from my_spdb.models import Server, Application, Role
from spdb.base import SPDB
class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    """With lists under the same name as model"""
    models = [Server, Application, Role]
```

## File: my_spdb/models.py
```python
from pydantic import BaseModel, Field
from typing import List, Optional
class Role(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    description: Optional[str] = Field(None, alias="Description")
class Application(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    version: Optional[str] = Field(None, alias="Version")
    language: Optional[str] = Field(None, alias="Language")
    is_active: bool = Field(True, alias="Is Active")
class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    ip_address: Optional[str] = Field(None, alias="Ip Address")
    operating_system: Optional[str] = Field(None, alias="Operating System")
    application: Application = Field(..., alias="Application")
    roles: list[Role] = Field(default_factory=list, alias="Roles")
    location: Optional[str] = Field(None, alias="Location")
    is_virtual: bool = Field(False, alias="Is Virtual")
```

## File: spdb/base.py
```python
from typing import TypeVar, Any, Union
from pydantic import BaseModel
from spdb.provider import SharePointProvider
from spdb.expander import Expander
TModel = TypeVar("TModel", bound=BaseModel)
class SPDB:
    """
    SPDB allows reading SharePoint lists as Pydantic models with lazy and full expansion.
    Example usage:
        spdb = SPDB(provider, models=[Device, Application])
        devices = spdb.get(Device)  # Not expanded
        devices[0].application  # -> str
        devices_exp = spdb.get(Device, expand=True)
        devices_exp[0].application.name  # -> expanded Application model
    """
    def __init__(self, provider: SharePointProvider, models: list[type[BaseModel]]):
        self.provider = provider
        self.models: dict[str, type[BaseModel]] = {m.__name__: m for m in models}
        self._cache: dict[str, list[BaseModel]] = {}
    def get_model(
        self, model_cls: type[TModel], expand: bool = False
    ) -> list[TModel]:
        model_name = model_cls.__name__
        if model_name not in self._cache:
            raw = self.provider.get_data(model_name)
            expander = Expander(model_cls, raw, related_data=self._get_related_data())
            self._cache[model_name] = expander.expand_all(expand=False)
        if not expand:
            return self._cache[model_name]  # type: ignore
        # Perform expansion now
        expander = Expander(model_cls, [m.model_dump() for m in self._cache[model_name]], self._get_related_data())
        return expander.expand_all(expand=True)
    def _get_related_data(self) -> dict[str, dict[str, BaseModel]]:
        related_data = {}
        for model_name, model_cls in self.models.items():
            if model_name not in self._cache:
                raw = self.provider.get_data(model_name)
                expander = Expander(model_cls, raw, related_data={})
                self._cache[model_name] = expander.expand_all(expand=False)
            by_name = {m.model_dump().get("name"): m for m in self._cache[model_name]}
            related_data[model_name] = by_name
        return related_data
```

## File: spdb/expander.py
```python
from typing import TypeVar, Any
from pydantic import BaseModel
TModel = TypeVar("TModel", bound=BaseModel)
def detect_related_fields(model_cls: type[TModel]) -> dict[str, type[BaseModel]]:
    related_fields = {}
    for fname, field in model_cls.model_fields.items():
        annotation = field.annotation
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            related_fields[fname] = annotation
    return related_fields
class Expander:
    """
    Expands model fields that reference other models using string identifiers.
    Supports lazy expansion by default.
    Usage:
        expander = Expander(model_cls, raw_data_list, related_models_by_name)
        expanded_models = expander.expand_all(expand=True)  # expand related models
        raw_models = expander.expand_all(expand=False)      # don't expand, use plain names
    """
    def __init__(
        self,
        model_cls: type[TModel],
        raw_data_list: list[dict[str, Any]],
        related_data: dict[str, dict[str, BaseModel]],
    ):
        self.model_cls = model_cls
        self.raw_data_list = raw_data_list
        self.related_data = related_data
        self._related_model_fields = detect_related_fields(self.model_cls)
    def expand_all(self, expand: bool = False) -> list[TModel]:
        output = []
        for row in self.raw_data_list:
            parsed = self._expand_single(row, expand=expand)
            output.append(parsed)
        return output
    def _expand_single(self, row: dict[str, Any], expand: bool) -> TModel:
        if not expand:
            return self.model_cls(**row)
        expanded = row.copy()
        for field, rel_model in self._related_model_fields.items():
            ref = row.get(field)
            if isinstance(ref, str):
                rel_name = rel_model.__name__
                resolved = self.related_data.get(rel_name, {}).get(ref)
                if resolved:
                    expanded[field] = resolved
        return self.model_cls(**expanded)
```

## File: spdb/model.py
```python
from pydantic import BaseModel as PydanticBaseModel
class BaseModel(PydanticBaseModel):
    pass
```

## File: spdb/provider.py
```python
# sharepoint_provider.py
import logging
from typing import Any, Optional
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
        verify: Optional[str] = None
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
        self._client_context = None
        self._authenticated = False
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
        if not self._client_context or not self._authenticated:
            logging.debug("Authenticating SharePoint client context.")
            self._authenticate()
        return self._client_context
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
                self._client_context = ClientContext(self.site_url, ctx_auth)
                self._authenticated = True
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
            list_name (str): The title of the SharePoint list.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing SharePoint list items.
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
    def clear_cache(self, list_name: Optional[str] = None):
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
