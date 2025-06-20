from pydantic import BaseModel, Field
from typing import Optional


class Role(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    description: Optional[str] = Field(None, alias="Description")


class Application(BaseModel):
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    version: Optional[str] = Field(None, alias="Version")
    language: Optional[str] = Field(None, alias="Language")
    is_active: bool = Field(True, alias="Is Active")


class Server(BaseModel):
    id: int = Field(..., alias="Id")
    hostname: str = Field(..., alias="Hostname")
    ip_address: Optional[str] = Field(None, alias="Ip Address")
    operating_system: Optional[str] = Field(None, alias="Operating System")
    application: Application = Field(..., alias="Application")
    roles: list[Role] = Field(default_factory=list, alias="Roles")
    location: Optional[str] = Field(None, alias="Location")
    is_virtual: bool = Field(False, alias="Is Virtual")
