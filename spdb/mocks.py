import json
import logging
from pathlib import Path
from typing import Any

from spdb.provider import SharePointProvider


class MockSharePointProvider(SharePointProvider):
    def __init__(self, mock_data_dir: str):
        self.mock_data_dir = Path(mock_data_dir)
        self._cache: dict[str, list[dict[str, Any]]] = {}
        logging.debug(f"Initialized MockSharePointProvider with data from {self.mock_data_dir}")

    def fetch_list_items(
        self,
        list_name: str,
        select: list[str] | None = None,
        expand: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Load mock data from a JSON file instead of querying SharePoint.

        The JSON file must be named <list_name>.json and contain a list of items.
        """
        file_path = self.mock_data_dir / f"{list_name}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Mock data file not found: {file_path}")

        logging.debug(f"Loading mock data for list '{list_name}' from {file_path}")

        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise TypeError(f"Mock data in {file_path} must be a list of dicts")

        return data
