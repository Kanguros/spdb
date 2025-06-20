# ruff: noqa: S101

import pytest

from my_spdb.core import MySPDB
from my_spdb.models import Application, Role, Server


@pytest.fixture(scope="module")
def myspdb():
    return MySPDB()


def test_myspdb_models(myspdb):
    assert myspdb.models == [Server, Application, Role]


@pytest.mark.parametrize("name", [Server, Application, Role])
def test_get_models(name: str, myspdb):
    items = myspdb.get_models(name=name)
    assert items and len(items) > 10
