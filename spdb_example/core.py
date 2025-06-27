from spdb.base import SPDB
from spdb.provider import SharePointProvider
from spdb_example.models import Application, Role, Server, Team


class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    """With lists under the same name as model"""
    models = [Server, Application, Role, Team]

    def __init__(self, username: str, password: str, verify=None):
        self.username = username
        self.password = password
        self.verify = verify
        super().__init__(
            SharePointProvider(
                self.url, self.username, password, verify=self.verify
            ),
            self.models,
        )
