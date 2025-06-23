from typing import Annotated

from pydantic import Field

from spdb.model import BaseModel


def test_no_relation():
    class TestModel(BaseModel):
        id: str
        name: str

    assert not TestModel.get_relation_fields()


def test_single_relation_no_union():
    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        child_first: TestModelRelated
        child_second: TestModelRelated
        id: str
        name: str

    TestModel_relation_fields = TestModel.get_relation_fields()
    assert "child_first" in TestModel_relation_fields.keys()
    assert (
        TestModel_relation_fields.get("child_first")
        == TestModelRelated.__name__
    )

    assert "child_second" in TestModel_relation_fields.keys()
    assert (
        TestModel_relation_fields.get("child_second")
        == TestModelRelated.__name__
    )

    assert not TestModelRelated.get_relation_fields()


def test_single_relation_with_union():
    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        id: str
        name: str
        child_first: TestModelRelated | str
        child_second: str | TestModelRelated

    TestModel_relation_fields = TestModel.get_relation_fields()
    assert "child_first" in TestModel_relation_fields.keys()
    assert (
        TestModel_relation_fields.get("child_first")
        == TestModelRelated.__name__
    )

    assert "child_second" in TestModel_relation_fields.keys()
    assert (
        TestModel_relation_fields.get("child_second")
        == TestModelRelated.__name__
    )

    assert not TestModelRelated.get_relation_fields()


def test_single_list_relation():
    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        id: str
        name: str
        child_first: list[TestModelRelated] | list[str]
        child_second: list[str] | list[TestModelRelated]
        last_param: bool = True

    TestModel_relation_fields = TestModel.get_relation_fields()
    assert "child_first" in TestModel_relation_fields
    assert (
        TestModel_relation_fields.get("child_first")
        == TestModelRelated.__name__
    )

    assert "child_second" in TestModel_relation_fields
    assert (
        TestModel_relation_fields.get("child_second")
        == TestModelRelated.__name__
    )

    assert not TestModelRelated.get_relation_fields()


def test_single_list_relation_annotated():
    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        id: str
        name: str
        child_first: Annotated[
            list[TestModelRelated] | list[str], Field(default_factory=list)
        ]
        child_second: list[str] | list[TestModelRelated]
        last_param: bool = True

    TestModel_relation_fields = TestModel.get_relation_fields()
    assert "child_first" in TestModel_relation_fields
    assert (
        TestModel_relation_fields.get("child_first")
        == TestModelRelated.__name__
    )

    assert "child_second" in TestModel_relation_fields
    assert (
        TestModel_relation_fields.get("child_second")
        == TestModelRelated.__name__
    )

    assert not TestModelRelated.get_relation_fields()
