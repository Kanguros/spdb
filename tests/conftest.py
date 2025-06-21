from pathlib import Path

import pytest

from my_spdb.core import MySPDB
from spdb.mocks import MockSharePointProvider


class MockMySPDB(MySPDB):
    def __init__(self, mock_data_dir):
        super().__init__(
            MockSharePointProvider(mock_data_dir=mock_data_dir), self.models
        )


@pytest.fixture(scope="module")
def my_mock_spdb():
    return MockMySPDB(Path("data"))
