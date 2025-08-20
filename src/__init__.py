"""
MongoDB Visualizer Application

A professional PyQt5-based desktop application for MongoDB database visualization
and management with robust connection handling, query execution, and data analysis.

Author: MongoDB Visualizer Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "MongoDB Visualizer Team"
__description__ = "Professional MongoDB Database Visualizer"

from .config.settings import get_config
from .utils.logging_config import initialize_logging, get_logger
from .controllers.database_controller import DatabaseController
from .models.data_models import ConnectionInfo, ApplicationState

# Initialize default configuration and logging
_config = get_config()
_log_manager = initialize_logging(_config)

__all__ = [
    'get_config',
    'initialize_logging', 
    'get_logger',
    'DatabaseController',
    'ConnectionInfo',
    'ApplicationState'
]
