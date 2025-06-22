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
        raw = self.provider.get_list_items(model_cls.get_list_name())
        processed = self._preprocess_sharepoint_data(raw, model_cls)
        return [model_cls(**item) for item in processed]

    def _preprocess_sharepoint_data(
        self, 
        raw_data: list[dict], 
        model_cls: type[TModel]
    ) -> list[dict]:
        """Convert SharePoint lookup fields to model-expected format.

        SharePoint returns lookup fields as {"Id": 1, "Title": "Name"}.
        This method converts them to simple strings for model compatibility.
        
        Args:
            raw_data: Raw data from SharePoint API.
            model_cls: Target model class for field mapping.
            
        Returns:
            Processed data suitable for Pydantic model instantiation.
        """
        relation_fields = model_cls.get_relation_fields()
        processed_data = []
        
        for item in raw_data:
            processed_item = {}
            
            for field_name, value in item.items():
                if field_name in relation_fields:
                    processed_item[field_name] = self._process_lookup_field(value)
                else:
                    processed_item[field_name] = value

            processed_data.append(processed_item)

        return processed_data

    def _process_lookup_field(self, lookup_value: Any) -> Any:
        """Convert SharePoint lookup field to simple value.

        Args:
            lookup_value: SharePoint lookup field value.

        Returns:
            Processed value (string for single lookup, list of strings for multi-lookup).
        """
        if lookup_value is None:
            return None

        if isinstance(lookup_value, dict) and "Title" in lookup_value:
            return lookup_value["Title"]

        if isinstance(lookup_value, list):
            return [
                item["Title"] if isinstance(item, dict) and "Title" in item else item
                for item in lookup_value
            ]

        return lookup_value

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

    def _expand(
        self,
        items: list[TModel],
        model_cls: type[TModel]
    ) -> list[TModel]:
        """Expand related model fields using identifier lookups.

        Args:
            items: List of model instances to expand.
            model_cls: Model class for relation field mapping.

        Returns:
            List of model instances with expanded relations.
        """
        self._ensure_lookups()
        relations = model_cls.get_relation_fields()
        expanded: list[TModel] = []

        for obj in items:
            updates: dict[str, Any] = {}
            data = obj.__dict__

            for field_name, rel_model_name in relations.items():
                key = data.get(field_name)
                lookup = self._lookups.get(rel_model_name, {})

                if isinstance(key, list):
                    expanded_items = [
                        lookup[item_key] for item_key in key
                        if item_key in lookup
                    ]
                    if expanded_items:
                        updates[field_name] = expanded_items
                elif key in lookup:
                    updates[field_name] = lookup[key]

            expanded.append(obj.model_copy(update=updates) if updates else obj)
        return expanded
