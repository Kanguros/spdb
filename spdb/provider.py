# sharepoint_provider.py

import logging
from typing import Any, Optional

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.caml import CamlQuery
from office365.sharepoint.lists.list import List as SPlist


class SharePointProvider:
    def __init__(
        self,
        site_url: str,
        username: str,
        password: str,
        verify: Optional[str] = None,
    ):
        """
        Initializes the SharePointProvider with authentication details and site URL.

        Args:
            site_url (str): The URL of the SharePoint site.
            username (str): Username for SharePoint authentication.
            password (str): Password for SharePoint authentication.
            verify (str | None): Path to SSL certificate for verification, or None to disable verification.
        """
        self.site_url = site_url
        self.username = username
        self.password = password
        self.verify = verify
        self._client_context = None
        self._authenticated = False

        if not self.username or not self.password:
            raise ValueError("Username and password must be provided")

        logging.debug(
            f"SharePointProvider initialized for site '{self.site_url}' with user '{self.username}'."
        )

    @property
    def client_context(self) -> ClientContext:
        """
        Returns the authenticated SharePoint client context.

        Returns:
            ClientContext: Authenticated SharePoint client context.
        """
        if not self._client_context or not self._authenticated:
            logging.debug("Authenticating SharePoint client context.")
            self._authenticate()
        return self._client_context

    def _authenticate(self):
        """
        Authenticates with SharePoint using the provided credentials.

        Raises:
            Exception: If authentication fails.
        """
        try:
            logging.debug(
                f"Attempting authentication for user '{self.username}' at '{self.site_url}'"
            )
            ctx_auth = AuthenticationContext(self.site_url)
            if ctx_auth.acquire_token_for_user(self.username, self.password):
                self._client_context = ClientContext(self.site_url, ctx_auth)
                self._authenticated = True
                logging.info("SharePoint authentication successful.")
            else:
                error_msg = ctx_auth.get_last_error()
                logging.error(f"SharePoint authentication failed: {error_msg}")
                raise Exception(f"Authentication failed: {error_msg}")
        except Exception as e:
            logging.error(f"SharePoint authentication error: {str(e)}")
            raise

    def get_list(self, list_name: str) -> SPlist:
        """
        Retrieves a SharePoint list by its name.

        Args:
            list_name (str): The name of the SharePoint list.

        Returns:
            SPlist: The SharePoint list object.
        """
        logging.debug(f"Fetching SharePoint list: '{list_name}'")
        return self.client_context.web.lists.get_by_title(list_name)

    def get_list_items(self, list_name: str) -> list[dict[str, Any]]:
        """
        Fetch all items from a SharePoint list. Uses in-memory cache if data was already retrieved.

        Args:
            list_name (str): The title of the SharePoint list.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing SharePoint list items.
        """
        if list_name in self._cache:
            return self._cache[list_name]

        sp_list = self.get_list(list_name)
        items = sp_list.get_items(CamlQuery())
        self.ctx.load(items)
        self.ctx.execute_query()

        parsed_items = [item.properties for item in items]
        self._cache[list_name] = parsed_items
        return parsed_items

    def clear_cache(self, list_name: Optional[str] = None):
        """
        Clears the internal cache.

        Args:
            list_name (Optional[str]): If provided, only clears the cache for the given list.
                                       If None, clears the entire cache.
        """
        if list_name:
            self._cache.pop(list_name, None)
        else:
            self._cache.clear()
