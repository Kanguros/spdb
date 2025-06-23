from spdb.model import BaseModel


def test_no_relation():
    class TestModel(BaseModel):
        id: str
        name: str

    model_relation_fields = TestModel.get_relation_fields()
    assert not model_relation_fields


def test_single_relation():
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

    TestModelRelated_relation_fields = TestModelRelated.get_relation_fields()
    assert not TestModelRelated_relation_fields


def test_single_list_relation():
    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        id: str
        name: str
        child_first: list[TestModelRelated] | list[str]
        child_second: list[str] | list[TestModelRelated]

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

    TestModelRelated_relation_fields = TestModelRelated.get_relation_fields()
    assert not TestModelRelated_relation_fields
