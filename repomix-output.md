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
- Files matching these patterns are excluded: **/**init**.py, tests/**, .gitignore, .pre-commit-config.yaml, poetry.lock, pyproject.toml, repomix.config.json, tests/\*_/_.json, mocks.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Empty lines have been removed from all files
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure

```
base.py
model.py
provider.py
```

# Files

## File: base.py

```python
from typing import Any
from spdb.model import BaseModel, TModel
from spdb.provider import SharePointProvider
class SPDB:
    """SharePoint Database abstraction layer.
    SPDB allows reading SharePoint lists as Pydantic models, supporting both lazy
    and full expansion of related fields. Related fields are detected automatically
    via Pydantic model annotations.
    Example:
        spdb = SPDB(provider, models=[Device, Application])
        devices = spdb.get_models(Device)
        devices_full = spdb.get_models(Device, expanded=True)
    """
    default_provider: type[SharePointProvider] = SharePointProvider
    def __init__(
        self,
        provider: SharePointProvider,
        models: list[type[BaseModel]],
    ):
        """Initialize SPDB with provider and model classes.
        Args:
            provider: SharePoint provider instance for data access.
            models: List of BaseModel classes representing SharePoint lists.
        """
        self.provider = provider
        self._models: dict[str, type[BaseModel]] = {
            m.__name__: m for m in models
        }
        self._cache: dict[str, list[BaseModel]] = {}
        self._lookups: dict[str, dict[Any, BaseModel]] = {}
    def get_models(
        self,
        model_cls: type[TModel],
        expanded: bool = False,
    ) -> list[TModel]:
        """Retrieve list of models of specified type.
        Args:
            model_cls: The Pydantic model class to load.
            expanded: If True, expand and hydrate all related fields.
        Returns:
            List of Pydantic model instances.
        """
        name = model_cls.__name__
        if name not in self._cache:
            self._cache[name] = self._load(model_cls)
        items = self._cache[name]
        if not expanded:
            return items
        return self._expand(items, model_cls)
    def _load(self, model_cls: type[TModel]) -> list[TModel]:
        """Load raw data from SharePoint into Pydantic models.
        Args:
            model_cls: The model class to instantiate.
        Returns:
            List of model instances without expanded relations.
        """
        items = self.provider.get_list_items(model_cls.get_list_name())
        return [model_cls(**item) for item in items]
    def _ensure_lookups(self) -> None:
        """Build lookup dictionaries for all registered models."""
        for model_name, model_cls in self._models.items():
            if model_name not in self._cache:
                self._cache[model_name] = self._load(model_cls)
            if model_name not in self._lookups:
                self._lookups[model_name] = {
                    getattr(obj, "name", obj.id): obj
                    for obj in self._cache[model_name]
                }
    def _expand(self, items, model_cls):
        """Expand related model fields into actual model instances."""
        self._ensure_lookups()
        relations = model_cls.get_relation_fields()
        expanded_items = []
        for obj in items:
            updates = {}
            for field_name, rel_model_name in relations.items():
                raw_val = getattr(obj, field_name)
                lookup = self._lookups.get(rel_model_name, {})
                if isinstance(raw_val, list):
                    expanded_list = [
                        lookup.get(item_key) for item_key in raw_val
                        if item_key in lookup
                    ]
                    if expanded_list:
                        updates[field_name] = expanded_list
                elif raw_val in lookup:
                    updates[field_name] = lookup[raw_val]
            if updates:
                obj = obj.model_copy(update=updates)
            expanded_items.append(obj)
        return expanded_items
```

## File: model.py

```python
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    TypeVar,
    get_args,
    get_origin,
    overload,
)
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from pydantic_core import core_schema
def extract_model_class(
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
class BaseModel(PydanticBaseModel):
    """Base Model"""
    _list_name: ClassVar[str | None] = None
    _relation_fields: ClassVar[dict[str, str]] = {}
    model_config = ConfigDict(
        use_enum_values=True,
        validate_by_name=True,
        validate_by_alias=True,
        use_attribute_docstrings=True,
        str_strip_whitespace=True,
    )
    @classmethod
    def get_list_name(cls) -> str:
        return cls._list_name or cls.__name__
    @classmethod
    def get_relation_fields(cls) -> dict[str, str]:
        """
        Return a mapping of field name to related class name for expandable fields.
        Supports both single and list of BaseModel relations.
        """
        if not cls._relation_fields:
            relations = {}
            for field_name, field_info in cls.model_fields.items():
                model_cls = extract_model_class(field_info.annotation)
                if model_cls:
                    relations[field_name] = model_cls.__name__
            cls._relation_fields = relations
        return cls._relation_fields
TModel = TypeVar("TModel", bound=BaseModel)
ValueType = TypeVar("ValueType")
class LookupField(Generic[TModel]):
    """Descriptor for SharePoint lookup fields with injectable parsing logic."""
    def __init__(
        self,
        model: type[TModel],
        *,
        validator: Callable | None = None,
        **field_kwargs
    ):
        """
        Args:
            model: Pydantic model class for the lookup target.
            alias: SharePoint field alias.
            validator: Optional function to transform raw API input.
        """
        self.model = model
        self.validator = validator or self._default_validator
        self.name: str
        self.field_kwargs = field_kwargs
    def __set_name__(self, owner: Any, name: str) -> None:
        owner.model_fields[name] = Field(**self.field_kwargs)
        self.name = name
    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "LookupField[TModel]": ...
    @overload
    def __get__(self, instance: Any, owner: type[Any]) -> ValueType: ...
    def __get__(self, instance: Any, owner: type[Any]) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value
    @staticmethod
    def _default_validator(val: Any) -> Any:
        """Convert SharePoint lookup to simple strings."""
        if val is None:
            return None
        if isinstance(val, dict) and "Title" in val:
            return val["Title"]
        if isinstance(val, list):
            return [item.get("Title", item) for item in val]
        return val
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Any
    ) -> Any:
        """Pydantic v2 core schema with injectable validator."""
        return core_schema.with_info_after_validator_function(
            handler(source),
            lambda v, info: cls._invoke_validator(info.field_name, v),
            field_name=handler.field_name,
        )
    @classmethod
    def _invoke_validator(cls, field_name: str, val: Any) -> Any:
        """Inner hook to call the instance’s validator."""
        # Resolve the LookupField instance to access its validator
        lookup_field: LookupField = getattr(cls, field_name)
        return lookup_field.validator(val)
```

## File: provider.py

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
        logging.debug(f"Fetching from '{sp_list}' items with {select=} {expand=}")
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
