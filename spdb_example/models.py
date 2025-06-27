from typing import Annotated

from pydantic import Field

from spdb.model import BaseModel, LookupField


class Role(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    description: Annotated[str, Field("", alias="Description")]


class Team(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    members: Annotated[list[str], Field(default_factory=list, alias="Members")]


class Application(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    name: Annotated[str, Field(..., alias="Name")]
    version: Annotated[str | None, Field(default=None, alias="Version")]
    language: Annotated[str | None, Field(default=None, alias="Language")]
    is_active: Annotated[bool, Field(default=True, alias="Is Active")]
    owner: Annotated[
        str | Team, LookupField, Field(default=None, alias="Owner")
    ]


class Server(BaseModel):
    id: Annotated[int, Field(..., alias="Id")]
    hostname: Annotated[str, Field(..., alias="Hostname")]
    application: Annotated[
        Application | str, Field(..., alias="Application"), LookupField
    ]
    ip_address: Annotated[str | None, Field(default=None, alias="Ip Address")]
    operating_system: Annotated[
        str | None, Field(None, alias="Operating System")
    ]
    roles: Annotated[
        list[str] | list[Role],
        Field(default_factory=list, alias="Roles"),
        LookupField,
    ]
    location: Annotated[str | None, Field(default=None, alias="Location")]
    is_virtual: Annotated[bool, Field(default=False, alias="Is Virtual")]
