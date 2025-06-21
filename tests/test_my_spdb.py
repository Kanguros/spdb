
from my_spdb.models import Application, Role, Server, Team
import pytest

MyModels = [Server, Application, Role, Team]

def test_myspdb_models(my_mock_spdb):
    assert my_mock_spdb.models == MyModels


@pytest.mark.parametrize("name", MyModels)
def test_get_models(name: str, my_mock_spdb):
    items = my_mock_spdb.get_models(name=name, expanded=True)
    assert items and len(items) > 10


def test_get_server_models_expanded(my_mock_spdb):
    servers = my_mock_spdb.get_models(name=Server, expanded=True)
    for server in servers:
        if server.application:
            assert isinstance(server.application, Application)
        if server.roles:
            assert all(isinstance(role, Role) for role in server.roles)
