from typing import Any

from spdb.model import BaseModel, TModel
from spdb.provider import SharePointProvider


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

    def get_models(
        self,
        model_cls: type[TModel],
        expanded: bool = False,
    ) -> list[TModel]:
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
        items = self._cache[name]
        if not expanded:
            return items
        return self._expand(items, model_cls)

    def _load(self, model_cls: type[TModel]) -> list[TModel]:
        """Load raw data from SharePoint into Pydantic models without expanding relations."""
        raw = self.provider.get_list_items(model_cls.get_list_name())
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

    def _expand(
        self, items: list[TModel], model_cls: type[TModel]
    ) -> list[TModel]:
        """Fully expand related model fields based on identifier lookups."""
        self._ensure_lookups()

        relations = model_cls.get_relation_fields()
        expanded: list[TModel] = []

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
