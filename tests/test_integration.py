"""Integration tests for SPDB error handling and edge cases."""
import pytest
from unittest.mock import Mock

from spdb.base import SPDB
from spdb.error import ModelLoadError
from spdb.mocks import MockSharePointProvider
from spdb_example.models import Server, Application


class TestSPDBErrorHandling:
    """Test error handling in SPDB operations."""

    def test_model_instantiation_failure(self, tmp_path):
        """Test handling of model instantiation failures."""
        # Create mock data with invalid structure
        mock_file = tmp_path / "Server.json"
        mock_file.write_text('[{"Id": "invalid_id", "InvalidField": "value"}]')
        
        provider = MockSharePointProvider(tmp_path)
        spdb = SPDB(provider, [Server])
        
        # Should handle invalid data gracefully by skipping bad records
        servers = spdb.get_model_items(Server)
        assert len(servers) == 0  # All records were invalid, so none loaded

    def test_provider_failure_handling(self):
        """Test handling of provider failures."""
        mock_provider = Mock()
        mock_provider.get_list_items.side_effect = Exception("Connection failed")
        
        spdb = SPDB(mock_provider, [Server])
        
        with pytest.raises(ModelLoadError):
            spdb.get_model_items(Server)

    def test_relationship_expansion_with_missing_data(self, tmp_path):
        """Test relationship expansion when referenced data is missing."""
        # Server references Application that doesn't exist
        server_file = tmp_path / "Server.json"
        server_file.write_text('''[{
            "Id": 1,
            "Hostname": "test-server",
            "Application": {"Id": 999, "Title": "Missing App"}
        }]''')
        
        app_file = tmp_path / "Application.json"
        app_file.write_text('[{"Id": 1, "Name": "Real App"}]')
        
        provider = MockSharePointProvider(tmp_path)
        spdb = SPDB(provider, [Server, Application])
        
        servers = spdb.get_model_items(Server, expanded=True)
        # Should handle missing references gracefully
        assert len(servers) == 1
        assert servers[0].application is None or isinstance(servers[0].application, str)


class TestSPDBPerformance:
    """Test performance characteristics and optimization."""
    
    def test_caching_effectiveness(self, tmp_path):
        """Test that caching reduces provider calls."""
        mock_file = tmp_path / "Server.json"
        mock_file.write_text('[{"Id": 1, "Hostname": "test", "Application": {"Id": 1, "Title": "Test App"}}]')

        provider = MockSharePointProvider(tmp_path)
        spdb = SPDB(provider, [Server])

        # Mock the provider to count calls
        original_method = provider.get_list_items
        call_count = 0

        def counting_get_list_items(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_method(*args, **kwargs)

        provider.get_list_items = counting_get_list_items

        # Multiple calls should only result in one provider call
        spdb.get_model_items(Server)
        spdb.get_model_items(Server)
        spdb.get_model_items(Server, expanded=True)

        assert call_count == 1  # Only one actual fetch    def test_large_dataset_handling(self, tmp_path):
        """Test handling of large datasets."""
        # Generate large mock dataset
        large_data = [{"Id": i, "Hostname": f"server-{i:04d}", "Application": {"Id": 1, "Title": "Test App"}} for i in range(1000)]
        mock_file = tmp_path / "Server.json"
        import json
        mock_file.write_text(json.dumps(large_data))

        provider = MockSharePointProvider(tmp_path)
        spdb = SPDB(provider, [Server])

        servers = spdb.get_model_items(Server)
        assert len(servers) == 1000

        # Test ID-based lookup efficiency
        subset = spdb.get_models_by_ids(Server, [1, 2, 3])
        assert len(subset) == 3
        assert all(server.id in [1, 2, 3] for server in subset)
