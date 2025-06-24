import pytest

from my_spdb.models import Application, Role, Server, Team


def check_expanded_server(server: Server):
    if server.application:
        assert isinstance(server.application, Application)
    if server.roles:
        print(f"{server.roles=}")
        assert all(isinstance(role, Role) for role in server.roles)


MyModels = [
    {"model": Server, "count": 20, "check_func": check_expanded_server},
    {"model": Application, "count": 5, "check_func": None},
    {"model": Role, "count": 10, "check_func": None},
    {"model": Team, "count": 3, "check_func": None},
]


def test_myspdb_models(my_mock_spdb):
    assert my_mock_spdb.models == [m["model"] for m in MyModels]


@pytest.mark.parametrize("my_model", MyModels)
def test_get_models(my_model, my_mock_spdb):
    items = my_mock_spdb.get_models(my_model["model"], expanded=False)
    assert items and len(items) == my_model["count"]


@pytest.mark.parametrize("my_model", MyModels)
def test_get_server_models_expanded(my_model, my_mock_spdb):
    items = my_mock_spdb.get_models(my_model["model"], expanded=True)
    assert items and len(items) == my_model["count"]
    check_func = my_model["check_func"]
    if check_func is not None:
        for item in items:
            check_func(item)
