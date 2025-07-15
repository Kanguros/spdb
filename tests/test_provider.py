"""Tests for SharePointProvider and MockSharePointProvider."""
import pytest
from unittest.mock import Mock, patch

from spdb.provider import SharePointProvider, ProviderError
from spdb.mocks import MockSharePointProvider


class TestSharePointProvider:
    """Test SharePointProvider authentication and data access."""

    def test_init_requires_credentials(self):
        """Test that username and password are required."""
        with pytest.raises(ValueError, match="Username and password must be provided"):
            SharePointProvider("https://site.com", "", "password")

        with pytest.raises(ValueError, match="Username and password must be provided"):
            SharePointProvider("https://site.com", "user", "")

    def test_authentication_failure(self):
        """Test authentication failure handling."""
        provider = SharePointProvider("https://site.com", "user", "password")
        
        with patch('spdb.provider.AuthenticationContext') as mock_auth:
            mock_auth_instance = Mock()
            mock_auth_instance.with_credentials.return_value = False
            mock_auth_instance.get_last_error.return_value = "Invalid credentials"
            mock_auth.return_value = mock_auth_instance
            
            with pytest.raises(ProviderError, match="Authentication failed"):
                _ = provider.ctx

    def test_cache_functionality(self):
        """Test that caching works correctly."""
        provider = SharePointProvider("https://site.com", "user", "password")
        
        # Mock the fetch_list_items method
        with patch.object(provider, 'fetch_list_items') as mock_fetch:
            mock_fetch.return_value = [{"Id": 1, "Name": "Test"}]
            
            # First call should fetch from SharePoint
            result1 = provider.get_list_items("TestList")
            assert mock_fetch.call_count == 1
            
            # Second call should return cached data
            result2 = provider.get_list_items("TestList")
            assert mock_fetch.call_count == 1  # No additional calls
            assert result1 == result2

    def test_clear_cache(self):
        """Test cache clearing functionality."""
        provider = SharePointProvider("https://site.com", "user", "password")
        provider._cache = {"TestList": [{"Id": 1}], "OtherList": [{"Id": 2}]}
        
        # Clear specific list cache
        provider.clear_cache("TestList")
        assert "TestList" not in provider._cache
        assert "OtherList" in provider._cache
        
        # Clear all cache
        provider.clear_cache()
        assert len(provider._cache) == 0


class TestMockSharePointProvider:
    """Test MockSharePointProvider for development and testing."""

    def test_missing_mock_file(self, tmp_path):
        """Test error handling when mock file doesn't exist."""
        mock_provider = MockSharePointProvider(tmp_path)
        
        with pytest.raises(FileNotFoundError):
            mock_provider.fetch_list_items("NonExistentList")

    def test_invalid_mock_data(self, tmp_path):
        """Test error handling when mock file contains invalid data."""
        mock_file = tmp_path / "InvalidList.json"
        mock_file.write_text('{"not": "a list"}')
        
        mock_provider = MockSharePointProvider(tmp_path)
        
        with pytest.raises(TypeError, match="Mock data .* must be a list"):
            mock_provider.fetch_list_items("InvalidList")

    def test_successful_mock_load(self, tmp_path):
        """Test successful loading of mock data."""
        mock_file = tmp_path / "TestList.json"
        mock_file.write_text('[{"Id": 1, "Name": "Test Item"}]')
        
        mock_provider = MockSharePointProvider(tmp_path)
        result = mock_provider.fetch_list_items("TestList")
        
        assert len(result) == 1
        assert result[0]["Id"] == 1
        assert result[0]["Name"] == "Test Item"
