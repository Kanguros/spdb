# # test_sharepoint_provider.py

# import pytest
# from unittest.mock import MagicMock, patch

# from spdb.provider import SharePointProvider


# @pytest.fixture
# def provider():
#     return SharePointProvider(
#         site_url="https://example.sharepoint.com/sites/test",
#         username="user",
#         password="pass",
#     )


# def mock_items(properties_list):
#     """Helper to create a mock items list with .properties attribute."""

#     class MockItem:
#         def __init__(self, properties):
#             self.properties = properties

#     return [MockItem(props) for props in properties_list]


# @patch("sharepoint_provider.ClientContext")
# @patch("sharepoint_provider.AuthenticationContext")
# def test_authentication_success(mock_auth_ctx, mock_client_ctx, provider):
#     mock_auth = MagicMock()
#     mock_auth.acquire_token_for_user.return_value = True
#     mock_auth_ctx.return_value = mock_auth

#     provider._client_context = None
#     provider._authenticated = False
#     provider._authenticate()

#     assert provider._authenticated is True
#     assert provider._client_context is not None


# @patch("sharepoint_provider.ClientContext")
# @patch("sharepoint_provider.AuthenticationContext")
# def test_authentication_failure(mock_auth_ctx, mock_client_ctx, provider):
#     mock_auth = MagicMock()
#     mock_auth.acquire_token_for_user.return_value = False
#     mock_auth.get_last_error.return_value = "Invalid credentials"
#     mock_auth_ctx.return_value = mock_auth

#     provider._client_context = None
#     provider._authenticated = False

#     with pytest.raises(Exception) as exc:
#         provider._authenticate()
#     assert "Authentication failed" in str(exc.value)


# @patch(
#     "sharepoint_provider.SharePointProvider.client_context",
#     new_callable=MagicMock,
# )
# def test_get_list(mock_client_context, provider):
#     mock_lists = MagicMock()
#     mock_list = MagicMock()
#     mock_lists.get_by_title.return_value = mock_list
#     mock_client_context.web.lists = mock_lists

#     result = provider.get_list("TestList")
#     assert result == mock_list
#     mock_lists.get_by_title.assert_called_once_with("TestList")


# @patch("sharepoint_provider.SharePointProvider.get_list")
# def test_fetch_items_basic(mock_get_list, provider):
#     mock_sp_list = MagicMock()
#     mock_items_list = mock_items(
#         [{"Id": 1, "Title": "A"}, {"Id": 2, "Title": "B"}]
#     )
#     mock_query = MagicMock()
#     mock_query.get.return_value.execute_query.return_value = mock_items_list
#     mock_sp_list.items = mock_query
#     mock_get_list.return_value = mock_sp_list

#     result = provider.fetch_items_basic("TestList")
#     assert isinstance(result, list)
#     assert result == [{"Id": 1, "Title": "A"}, {"Id": 2, "Title": "B"}]


# @patch("sharepoint_provider.SharePointProvider.get_list")
# def test_fetch_items_expanded(mock_get_list, provider):
#     mock_sp_list = MagicMock()
#     mock_items_list = mock_items(
#         [
#             {"Id": 1, "Title": "A", "Related": {"Id": 10, "Name": "RelA"}},
#             {"Id": 2, "Title": "B", "Related": {"Id": 20, "Name": "RelB"}},
#         ]
#     )
#     mock_query = MagicMock()
#     mock_query.expand.return_value = mock_query
#     mock_query.select.return_value = mock_query
#     mock_query.get.return_value.execute_query.return_value = mock_items_list
#     mock_sp_list.items = mock_query
#     mock_get_list.return_value = mock_sp_list

#     expand_fields = ["Related"]
#     select_fields = ["Id", "Title", "Related/Id", "Related/Name"]
#     result = provider.fetch_items_expanded(
#         "TestList", expand_fields, select_fields
#     )
#     assert isinstance(result, list)
#     assert result[0]["Related"]["Id"] == 10
#     assert result[1]["Related"]["Name"] == "RelB"


# @patch("sharepoint_provider.SharePointProvider.get_list")
# def test_fetch_items_with_select_and_expand(mock_get_list, provider):
#     mock_sp_list = MagicMock()
#     mock_items_list = mock_items([{"Id": 1, "Title": "A", "X": 5}])
#     mock_query = MagicMock()
#     mock_query.expand.return_value = mock_query
#     mock_query.select.return_value = mock_query
#     mock_query.get.return_value.execute_query.return_value = mock_items_list
#     mock_sp_list.items = mock_query
#     mock_get_list.return_value = mock_sp_list

#     result = provider.fetch_items(
#         "TestList", expand_fields=["X"], select_fields=["Id", "Title", "X"]
#     )
#     assert isinstance(result, list)
#     assert result[0]["X"] == 5
