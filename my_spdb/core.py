from my_spdb.models import Server, Application, Role
from spdb.base import SPDB


class MySPDB(SPDB):
    url = "https://address_to_sharepoint/site/"
    """With lists under the same name as model"""
    models = [Server, Application, Role]
