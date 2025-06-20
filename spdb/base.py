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
