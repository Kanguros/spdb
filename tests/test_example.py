import pytest

from spdb_example.models import Application, Role, Server, Team

MODELS = (Server, Application, Role, Team)

SERVER_PARAMS = (Server, 20)
APPLICATION_PARAMS = (Application, 5)
ROLE_PARAMS = (Role, 10)
TEAM_PARAMS = (Team, 3)


def test_myspdb_models(my_mock_spdb):
    assert my_mock_spdb.models == list(MODELS)


@pytest.mark.parametrize(
    "model_type,model_count",
    [SERVER_PARAMS, APPLICATION_PARAMS, ROLE_PARAMS, TEAM_PARAMS],
)
def test_get_models(model_type, model_count, my_mock_spdb):
    items = my_mock_spdb.get_model_items(model_type, expanded=False)
    assert items and len(items) == model_count
    for item in items:
        for _, value in item:
            assert not isinstance(value, MODELS), (
                f"Unexpected model type: {type(value)}"
            )


def test_get_server_expanded(my_mock_spdb):
    model_type, model_count = SERVER_PARAMS
    servers = my_mock_spdb.get_model_items(model_type, expanded=True)
    assert servers and len(servers) == model_count
    for server in servers:
        if server.application:
            assert isinstance(server.application, Application)
        if server.roles:
            assert all(isinstance(role, Role) for role in server.roles)


def test_get_application_expanded(my_mock_spdb):
    model_type, model_count = APPLICATION_PARAMS
    applications = my_mock_spdb.get_model_items(model_type, expanded=True)
    assert applications and len(applications) == model_count
    for application in applications:
        if application.owner:
            assert isinstance(application.owner, Team), (
                f"Expected Team, got {type(application.owner)}"
            )


def test_get_role_expanded(my_mock_spdb):
    model_type, model_count = ROLE_PARAMS
    roles = my_mock_spdb.get_model_items(model_type, expanded=True)
    assert roles and len(roles) == model_count
    for role in roles:
        for _, value in role:
            assert not isinstance(value, MODELS), (
                f"Unexpected model type: {type(value)}"
            )


def test_get_team_expanded(my_mock_spdb):
    model_type, model_count = TEAM_PARAMS
    teams = my_mock_spdb.get_model_items(model_type, expanded=True)
    assert teams and len(teams) == model_count
    for team in teams:
        for _, value in team:
            assert not isinstance(value, MODELS), (
                f"Unexpected model type: {type(value)}"
            )
