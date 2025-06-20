from typing import Any, TypeVar

from pydantic import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


def detect_related_fields(
    model_cls: type[TModel],
) -> dict[str, type[BaseModel]]:
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
