from typing import Any, ClassVar, TypeVar, get_args, get_origin

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


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
                model_cls = cls._extract_model_class(field_info.annotation)
                if model_cls:
                    relations[field_name] = model_cls.__name__
            cls._relation_fields = relations
        return cls._relation_fields

    @staticmethod
    def _extract_model_class(
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


TModel = TypeVar("TModel", bound=BaseModel)
