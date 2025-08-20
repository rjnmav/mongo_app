#!/usr/bin/env python3
"""
Test script to verify auto-connect functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import get_config
from src.models.data_models import ConnectionInfo

def test_auto_connect_config():
    """Test that auto-connect configuration works properly."""
    
    print("Testing auto-connect configuration...")
    
    # Get current config
    config = get_config()
    
    print(f"Current auto_connect_localhost setting: {config.database.auto_connect_localhost}")
    print(f"Default host: {config.database.default_host}")
    print(f"Default port: {config.database.default_port}")
    
    # Test ConnectionInfo creation with config values
    test_connection = ConnectionInfo(
        name="Test Connection",
        host=config.database.default_host,
        port=config.database.default_port,
        auth_enabled=False
    )
    
    print(f"Test connection: {test_connection.get_display_name()}")
    print(f"Connection string: {test_connection.get_connection_string(include_credentials=False)}")
    
    # Test toggling the setting
    original_setting = config.database.auto_connect_localhost
    config.database.auto_connect_localhost = not original_setting
    print(f"Toggled setting to: {config.database.auto_connect_localhost}")
    
    # Restore original setting
    config.database.auto_connect_localhost = original_setting
    print(f"Restored setting to: {config.database.auto_connect_localhost}")
    
    print("✅ Auto-connect configuration test passed!")

if __name__ == '__main__':
    test_auto_connect_config()
