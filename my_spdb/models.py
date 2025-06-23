from typing import Annotated

from pydantic import Field

from spdb.model import BaseModel, LookupField


class Role(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    description: str | None = Field(None, alias="Description")


class Team(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    members: list[str] = Field(default_factory=list, alias="Members")


class Application(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    version: str | None = Field(default=None, alias="Version")
    language: str | None = Field(default=None, alias="Language")
    is_active: bool = Field(default=True, alias="Is Active")
    owner: Team | str | None = Field(default=None, alias="Owner")
    owner: Annotated[str | Team, LookupField]


class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    application: Annotated[
        Application | str, Field(..., alias="Application"), LookupField
    ]
    ip_address: str | None = Field(default=None, alias="Ip Address")
    operating_system: str | None = Field(None, alias="Operating System")
    roles: Annotated[
        list[Role] | list[str],
        Field(default_factory=list, alias="Roles"),
        LookupField,
    ]
    location: str | None = Field(default=None, alias="Location")
    is_virtual: bool = Field(default=False, alias="Is Virtual")
