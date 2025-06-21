

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
        child: TestModelRelated

    TestModel_relation_fields = TestModel.get_relation_fields()
    print(TestModel_relation_fields)
    assert "child" in TestModel_relation_fields.keys()
    assert TestModelRelated.__name__ in TestModel_relation_fields.values()

    TestModelRelated_relation_fields = TestModelRelated.get_relation_fields()
    assert not TestModelRelated_relation_fields


def test_single_list_relation():

    class TestModelRelated(BaseModel):
        id: str
        name: str

    class TestModel(BaseModel):
        id: str
        name: str
        child: list[TestModelRelated]

    TestModel_relation_fields = TestModel.get_relation_fields()
    print(TestModel_relation_fields)
    assert "child" in TestModel_relation_fields.keys()
    assert TestModelRelated.__name__ in TestModel_relation_fields.values()

    TestModelRelated_relation_fields = TestModelRelated.get_relation_fields()
    assert not TestModelRelated_relation_fields
