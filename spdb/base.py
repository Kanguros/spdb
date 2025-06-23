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
        raw_items = self.provider.get_list_items(model_cls.get_list_name())
        loaded: list[TModel] = []

        for item_data in raw_items:
            instance = model_cls(**item_data)
            for rel_field in model_cls.get_relation_fields().keys():
                value = getattr(instance, rel_field)
                instance.__dict__[rel_field] = value
            loaded.append(instance)

        return loaded

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
        self._ensure_lookups()
        relations = model_cls.get_relation_fields()
        print(f"Expanding {model_cls=} {relations=}")
        expanded_items = []

        for obj in items:
            updates = {}
            for field_name, rel_model_name in relations.items():
                raw_val = getattr(obj, field_name)
                lookup = self._lookups.get(rel_model_name, {})
                if isinstance(raw_val, list):
                    expanded_list = [
                        lookup[item_key]
                        for item_key in raw_val
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
