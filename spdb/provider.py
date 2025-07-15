import logging
from typing import Any

from office365.runtime.auth.authentication_context import (
    AuthenticationContext,
    UserCredential,
)
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list import List as SPlist


class ProviderError(ValueError):
    pass


class SharePointProvider:
    def __init__(
        self,
        site_url: str,
        username: str,
        password: str,
        verify: str | None = None,
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

        self._ctx = None
        self._authenticated = False

        self._cache = {}

        if not self.username or not self.password:
            raise ValueError("Username and password must be provided")

        logging.debug(
            f"SharePointProvider initialized for site '{self.site_url}' with user '{self.username}'."
        )

    @property
    def ctx(self) -> ClientContext:
        """
        Returns the authenticated SharePoint client context.

        Returns:
            ClientContext: Authenticated SharePoint client context.
        """
        if not self._ctx or not self._authenticated:
            logging.debug(
                f"Attempting authentication for user '{self.username}' at '{self.site_url}'"
            )
            self._ctx = self._authenticate()
            logging.info("SharePoint authentication successful.")
            self._authenticated = True
        return self._ctx

    def _authenticate(self) -> ClientContext:
        """
        Authenticates with SharePoint using the provided credentials.

        Raises:
            ProviderError: If authentication fails.
        """
        try:
            ctx_auth = AuthenticationContext(self.site_url, allow_ntlm=True)
            if ctx_auth.with_credentials(
                UserCredential(self.username, self.password)
            ):
                return ClientContext(self.site_url, ctx_auth)
            error_msg = ctx_auth.get_last_error()
            raise ProviderError(f"Authentication failed: {error_msg}")  # noqa: TRY301
        except Exception as e:
            logging.error(f"SharePoint authentication error: {str(e)}")
            raise

    def fetch_list(self, list_name: str) -> SPlist:
        """
        Fetches a SharePoint list by its name.

        Args:
            list_name: The name of the SharePoint list.

        Returns:
            The SharePoint list object.
        """
        logging.debug(f"Fetching SharePoint list: '{list_name}'")
        return self.ctx.web.lists.get_by_title(list_name)

    def fetch_list_items(
        self,
        list_name: str,
        select: list[str] | None = None,
        expand: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch all items from a SharePoint list.

        Args:
            list_name: The title of the SharePoint list.

        Returns:
            A list of dictionaries representing SharePoint list items.
        """
        sp_list = self.fetch_list(list_name)
        select_arg = ["*"] if select is None else select
        logging.debug(
            f"Fetching from '{sp_list}' items with {select=} {expand=}"
        )
        items = sp_list.get().select(select_arg).expand(expand).execute_query()
        return [item.properties for item in items]

    def get_list_items(
        self,
        list_name: str,
    ) -> list[dict[str, Any]]:
        """
        Get all items from a SharePoint list. Uses in-memory cache if data was already retrieved.

        Args:
            list_name: The title of the SharePoint list.

        Returns:
            A list of dictionaries representing SharePoint list items.
        """
        if list_name in self._cache:
            return self._cache[list_name]
        items = self.fetch_list_items(list_name)
        self._cache[list_name] = items
        return items

    def clear_cache(self, list_name: str | None = None) -> None:
        """
        Clears the internal cache.

        Args:
            list_name: If provided, only clears the cache for the given list.
                        If None, clears the entire cache.
        """
        if list_name:
            self._cache.pop(list_name, None)
        else:
            self._cache.clear()
