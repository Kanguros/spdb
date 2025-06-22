from pydantic import BaseModel, Field


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


class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    ip_address: str | None = Field(default=None, alias="Ip Address")
    operating_system: str | None = Field(None, alias="Operating System")
    application: Application | str = Field(..., alias="Application")
    roles: list[Role] | list[str] = Field(default_factory=list, alias="Roles")
    location: str | None = Field(default=None, alias="Location")
    is_virtual: bool = Field(default=False, alias="Is Virtual")
