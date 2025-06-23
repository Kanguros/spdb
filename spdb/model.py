from types import UnionType
from typing import (
    Annotated,
    Any,
    ClassVar,
    TypeVar,
    get_args,
    get_origin,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import BeforeValidator, ConfigDict


def extract_model_class(
    annotation: Any,
) -> type[PydanticBaseModel] | None:
    """Identify and return a Pydantic BaseModel subclass from a type annotation.

    This function recursively inspects `annotation`, unwrapping
    `Annotated`, `Union`/`UnionType`, and `list` to find and return the
    first subclass of `PydanticBaseModel`. If no such subclass is found,
    returns None.

    Args:
        annotation: A type annotation that may include nested wrappers.

    Returns:
        The Pydantic model class found in the annotation or None.
    """
    origin = get_origin(annotation)
    args = get_args(annotation)
    if isinstance(annotation, type) and issubclass(
        annotation, PydanticBaseModel
    ):
        return annotation
    if origin is Annotated and args:
        return extract_model_class(args[0])
    if origin is UnionType:
        for arg in args:
            related = extract_model_class(arg)
            if related:
                return related
        return None
    if origin is list and args:
        return extract_model_class(args[0])
    return None


class BaseModel(PydanticBaseModel):
    """Base Model"""

    _list_name: ClassVar[str | None] = None

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
        """Get mapping of relation field names to target model class names."""
        cache_key = f"__{cls.__name__}_relation_fields__"
        if not hasattr(cls, cache_key):
            relations = {}
            for field_name, field_info in cls.model_fields.items():
                model_cls = extract_model_class(field_info.annotation)
                if model_cls:
                    relations[field_name] = model_cls.__name__
            setattr(cls, cache_key, relations)
        return getattr(cls, cache_key)


TModel = TypeVar("TModel", bound=BaseModel)


def lookup(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict) and "Title" in value:
        return value["Title"]
    if isinstance(value, list):
        return [item.get("Title", item) for item in value]
    return value


LookupField = BeforeValidator(lookup)
