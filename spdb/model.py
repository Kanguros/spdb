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

