import logging
from typing import Any

from spdb.error import ModelLoadError
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
        self, provider: SharePointProvider, models: list[type[TModel]]
    ):
        """Initialize SPDB with provider and model classes.

        Args:
            provider: SharePoint provider instance for data access.
            models: List of BaseModel classes representing SharePoint lists.
        """
        self.provider = provider
        self._models: dict[str, type[TModel]] = {m.__name__: m for m in models}
        self._cache: dict[str, list[TModel]] = {}
        self._lookups: dict[str, dict[Any, TModel]] = {}

    def get_model_items(
        self,
        model_cls: type[TModel],
        expanded: bool = False,
    ) -> list[TModel]:
        """Retrieve list of models of specified type.

        Args:
            model_cls: The :class:`spdb.model.TModel` model subclass to load.
            expanded: If True, expand all related fields.

        Returns:
            List of Pydantic model instances.

        Raises:
            ValueError: If model_cls is not a registered model.
            ModelLoadError: If loading fails.
        """
        if not issubclass(model_cls, BaseModel):
            raise TypeError(
                f"model_cls must be a BaseModel subclass, got {type(model_cls)}"
            )

        if model_cls.__name__ not in self._models:
            raise ValueError(
                f"Model {model_cls.__name__} not registered with this SPDB instance"
            )

        name = model_cls.__name__
        if name not in self._cache:
            self._cache[name] = self.load_model_items(model_cls)
        items = self._cache[name]
        if not expanded:
            return items
        return self._expand(items, model_cls)

    def get_models_by_ids(
        self,
        model_cls: type[TModel],
        ids: list[int | str],
        expanded: bool = False,
    ) -> list[TModel]:
        """Retrieve specific models by their IDs for efficient lookups.

        Args:
            model_cls: The :class:`spdb.model.TModel` model subclass to load.
            ids: List of model IDs to retrieve.
            expanded: If True, expand all related fields.

        Returns:
            List of Pydantic model instances matching the IDs.
        """
        all_models = self.get_model_items(model_cls, expanded=expanded)
        id_set = set(ids)
        return [model for model in all_models if model.id in id_set]

    def load_model_items(self, model_cls: type[TModel]) -> list[TModel]:
        """Load raw data from SharePoint into Pydantic models.

        Args:
            model_cls: The model class to instantiate.

        Returns:
            List of model instances without expanded relations.

        Raises:
            ModelLoadError: If data retrieval from provider fails.
        """
        try:
            raw_items = self.provider.get_list_items(model_cls.get_list_name())
        except Exception as e:
            logging.error(
                f"Failed to retrieve data for {model_cls.__name__}: {e}"
            )
            raise ModelLoadError(
                f"Failed to retrieve data for {model_cls.__name__}: {e}"
            ) from e

        return self.build_model_items(model_cls, raw_items)

    def build_model_items(
        self, model_cls: type[TModel], raw_items: list[dict]
    ) -> list[TModel]:
        loaded = []
        for item_data in raw_items:
            try:
                instance = model_cls(**item_data)
                for rel_field in model_cls.get_relation_fields().keys():
                    value = getattr(instance, rel_field)
                    instance.__dict__[rel_field] = value
                loaded.append(instance)
            except Exception as e:
                logging.warning(
                    f"Skipping invalid {model_cls.__name__} item {item_data.get('Id', 'Unknown')}: {e}"
                )
        logging.info(
            f"Successfully loaded {len(loaded)} {model_cls.__name__} instances"
        )
        return loaded

    def _ensure_lookups(self) -> None:
        """Build lookup dictionaries for all registered models."""
        for model_name, model_cls in self._models.items():
            if model_name not in self._cache:
                self._cache[model_name] = self.load_model_items(model_cls)
            if model_name not in self._lookups:
                self._lookups[model_name] = {
                    getattr(obj, "name", obj.id): obj
                    for obj in self._cache[model_name]
                }

    def _expand(self, items, model_cls):
        self._ensure_lookups()
        relations = model_cls.get_relation_fields()
        expanded_items = []

        for obj in items:
            updates = self._expand_object_relations(obj, relations)
            if updates:
                obj = obj.model_copy(update=updates)
            expanded_items.append(obj)

        return expanded_items

    def _expand_object_relations(self, obj, relations):
        """Expand all relation fields for a single object."""
        updates = {}
        for field_name, rel_model_name in relations.items():
            raw_val = getattr(obj, field_name)
            lookup = self._lookups.get(rel_model_name, {})
            expanded = self._expand_field(raw_val, lookup)
            if expanded is not None:
                updates[field_name] = expanded
        return updates

    def _expand_field(self, raw_val, lookup):
        """Expand a single relation field value using the lookup."""
        if isinstance(raw_val, list):
            expanded_list = [
                lookup[item_key] for item_key in raw_val if item_key in lookup
            ]
            return expanded_list if expanded_list else None
        if raw_val in lookup:
            return lookup[raw_val]
        return None

    def refresh_cache(self, model_cls: type[BaseModel] | None = None) -> None:
        """Refresh cached data for specified model or all models.

        Args:
            model_cls: Specific model to refresh, or None to refresh all.
        """
        if model_cls:
            model_name = model_cls.__name__
            if model_name in self._cache:
                del self._cache[model_name]
            if model_name in self._lookups:
                del self._lookups[model_name]
        else:
            self._cache.clear()
            self._lookups.clear()
