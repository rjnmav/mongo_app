"""
Application configuration settings.

This module provides centralized configuration management for the MongoDB Visualizer
application, following the 12-factor app methodology for configuration management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from PyQt5.QtCore import QSettings


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    default_host: str = "localhost"
    default_port: int = 27017
    default_auth_db: str = "admin"
    connection_timeout: int = 5000
    socket_timeout: int = 5000
    server_selection_timeout: int = 5000
    max_pool_size: int = 50


@dataclass
class UIConfig:
    """User interface configuration."""
    window_width: int = 1400
    window_height: int = 900
    tree_width: int = 350
    json_font_family: str = "Consolas, Monaco, 'Courier New', monospace"
    json_font_size: int = 10
    table_alternating_rows: bool = True
    syntax_highlighting: bool = True
    auto_expand_tree: bool = True


@dataclass
class QueryConfig:
    """Query execution configuration."""
    default_limit: int = 100
    max_limit: int = 1000
    default_skip: int = 0
    query_timeout: int = 30000
    max_query_history: int = 50


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    console_enabled: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class ConfigManager:
    """
    Configuration manager for the MongoDB Visualizer application.
    
    Handles loading, saving, and accessing application configuration
    from multiple sources (files, environment variables, user settings).
    """
    
    def __init__(self):
        self.app_name = "MongoDBVisualizer"
        self.config_dir = Path.home() / ".mongodb_visualizer"
        self.config_file = self.config_dir / "config.json"
        self.settings = QSettings("MongoDBVisualizer", "Settings")
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize configuration
        self.database = DatabaseConfig()
        self.ui = UIConfig()
        self.query = QueryConfig()
        self.logging = LoggingConfig()
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self._update_config_from_dict(config_data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Load UI settings from QSettings
        self._load_ui_settings()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_data = {
            'database': asdict(self.database),
            'ui': asdict(self.ui),
            'query': asdict(self.query),
            'logging': asdict(self.logging)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config file: {e}")
    
    def save_ui_settings(self) -> None:
        """Save UI-specific settings to QSettings."""
        self.settings.setValue("geometry/width", self.ui.window_width)
        self.settings.setValue("geometry/height", self.ui.window_height)
        self.settings.setValue("geometry/tree_width", self.ui.tree_width)
        self.settings.setValue("ui/json_font_size", self.ui.json_font_size)
        self.settings.setValue("ui/auto_expand_tree", self.ui.auto_expand_tree)
        self.settings.sync()
    
    def _load_ui_settings(self) -> None:
        """Load UI settings from QSettings."""
        self.ui.window_width = self.settings.value("geometry/width", self.ui.window_width, type=int)
        self.ui.window_height = self.settings.value("geometry/height", self.ui.window_height, type=int)
        self.ui.tree_width = self.settings.value("geometry/tree_width", self.ui.tree_width, type=int)
        self.ui.json_font_size = self.settings.value("ui/json_font_size", self.ui.json_font_size, type=int)
        self.ui.auto_expand_tree = self.settings.value("ui/auto_expand_tree", self.ui.auto_expand_tree, type=bool)
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration objects from dictionary."""
        if 'database' in config_data:
            for key, value in config_data['database'].items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        if 'ui' in config_data:
            for key, value in config_data['ui'].items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)
        
        if 'query' in config_data:
            for key, value in config_data['query'].items():
                if hasattr(self.query, key):
                    setattr(self.query, key, value)
        
        if 'logging' in config_data:
            for key, value in config_data['logging'].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        # Database configuration
        if os.getenv('MONGO_HOST'):
            self.database.default_host = os.getenv('MONGO_HOST')
        if os.getenv('MONGO_PORT'):
            self.database.default_port = int(os.getenv('MONGO_PORT'))
        if os.getenv('MONGO_AUTH_DB'):
            self.database.default_auth_db = os.getenv('MONGO_AUTH_DB')
        
        # Logging configuration
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL').upper()
    
    def get_recent_connections(self) -> list:
        """Get list of recent database connections."""
        size = self.settings.beginReadArray("recent_connections")
        connections = []
        for i in range(size):
            self.settings.setArrayIndex(i)
            connection = {
                'name': self.settings.value("name", ""),
                'host': self.settings.value("host", ""),
                'port': self.settings.value("port", 27017, type=int),
                'auth_enabled': self.settings.value("auth_enabled", False, type=bool),
                'username': self.settings.value("username", ""),
                'auth_db': self.settings.value("auth_db", "admin")
            }
            connections.append(connection)
        self.settings.endArray()
        return connections
    
    def save_recent_connection(self, connection: Dict[str, Any]) -> None:
        """Save a recent database connection."""
        recent = self.get_recent_connections()
        
        # Remove existing connection with same host:port
        recent = [c for c in recent if not (c['host'] == connection['host'] and c['port'] == connection['port'])]
        
        # Add new connection at the beginning
        recent.insert(0, connection)
        
        # Keep only last 10 connections
        recent = recent[:10]
        
        # Save to settings
        self.settings.beginWriteArray("recent_connections")
        for i, conn in enumerate(recent):
            self.settings.setArrayIndex(i)
            self.settings.setValue("name", conn.get('name', ''))
            self.settings.setValue("host", conn.get('host', ''))
            self.settings.setValue("port", conn.get('port', 27017))
            self.settings.setValue("auth_enabled", conn.get('auth_enabled', False))
            self.settings.setValue("username", conn.get('username', ''))
            self.settings.setValue("auth_db", conn.get('auth_db', 'admin'))
        self.settings.endArray()
        self.settings.sync()


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config
