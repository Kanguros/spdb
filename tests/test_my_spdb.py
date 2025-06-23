import pytest

from my_spdb.models import Application, Role, Server, Team

MyModels = {Server: 20, Application: 5, Role: 10, Team: 3}


def check_expanded_server(server: Server):
    if server.application:
        assert isinstance(server.application, Application)
    if server.roles:
        print(f"{server.roles=}")
        assert all(isinstance(role, Role) for role in server.roles)


def test_myspdb_models(my_mock_spdb):
    assert my_mock_spdb.models == list(MyModels.keys())


@pytest.mark.parametrize("name,count", MyModels.items())
def test_get_models(name: str, count: int, my_mock_spdb):
    items = my_mock_spdb.get_models(name, expanded=False)
    assert items and len(items) == count


@pytest.mark.parametrize(
    "model_cls,count,check_func",
    [
        (Server, 20, check_expanded_server),
    ],
)
def test_get_server_models_expanded(my_mock_spdb, model_cls, count, check_func):
    items = my_mock_spdb.get_models(model_cls, expanded=True)
    assert items and len(items) == count
    for item in items:
        check_func(item)
