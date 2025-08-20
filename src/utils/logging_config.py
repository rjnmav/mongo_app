"""
Logging configuration and utilities.

This module provides centralized logging configuration for the MongoDB Visualizer
application with support for file and console logging, rotation, and structured output.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from PyQt5.QtCore import QObject, pyqtSignal


class QtLogHandler(logging.Handler, QObject):
    """Custom logging handler that emits Qt signals for GUI integration."""
    
    log_message = pyqtSignal(str, str)  # level, message
    
    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
    
    def emit(self, record):
        """Emit a log record as a Qt signal."""
        try:
            msg = self.format(record)
            self.log_message.emit(record.levelname, msg)
        except Exception:
            self.handleError(record)


class LogManager:
    """
    Centralized logging manager for the application.
    
    Provides structured logging with file rotation, console output,
    and optional Qt signal emission for GUI integration.
    """
    
    def __init__(self, config=None):
        self.config = config
        self.qt_handler: Optional[QtLogHandler] = None
        self.log_dir = Path.home() / ".mongodb_visualizer" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """Configure application logging."""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.handlers.clear()  # Remove existing handlers
        
        # Set logging level
        level = getattr(logging, self.config.logging.level if self.config else "INFO")
        root_logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            self.config.logging.format if self.config else
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Console handler
        if not self.config or self.config.logging.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if not self.config or self.config.logging.file_enabled:
            log_file = self.log_dir / "mongodb_visualizer.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.config.logging.max_file_size if self.config else 10*1024*1024,
                backupCount=self.config.logging.backup_count if self.config else 5,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            root_logger.addHandler(file_handler)
        
        # Qt handler for GUI integration
        self.qt_handler = QtLogHandler()
        self.qt_handler.setFormatter(formatter)
        self.qt_handler.setLevel(logging.WARNING)  # Only warnings and errors to GUI
        root_logger.addHandler(self.qt_handler)
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized")
        logger.info(f"Log files location: {self.log_dir}")
    
    def get_qt_handler(self) -> Optional[QtLogHandler]:
        """Get the Qt log handler for GUI integration."""
        return self.qt_handler
    
    def set_level(self, level: str) -> None:
        """Change the logging level dynamically."""
        numeric_level = getattr(logging, level.upper())
        logging.getLogger().setLevel(numeric_level)
        
        # Update all handlers
        for handler in logging.getLogger().handlers:
            if not isinstance(handler, QtLogHandler):
                handler.setLevel(numeric_level)
    
    def get_log_files(self) -> list:
        """Get list of available log files."""
        return list(self.log_dir.glob("*.log*"))
    
    def clear_logs(self) -> None:
        """Clear all log files."""
        for log_file in self.get_log_files():
            try:
                log_file.unlink()
                logging.info(f"Deleted log file: {log_file}")
            except Exception as e:
                logging.error(f"Failed to delete log file {log_file}: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class PerformanceTimer:
    """Context manager for timing operations and logging performance metrics."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Operation '{self.operation_name}' completed in {duration:.3f}s")
        else:
            self.logger.error(f"Operation '{self.operation_name}' failed after {duration:.3f}s: {exc_val}")


def log_method_calls(cls):
    """
    Class decorator to automatically log method calls.
    Useful for debugging and monitoring.
    """
    class Wrapper:
        def __init__(self, *args, **kwargs):
            self._wrapped = cls(*args, **kwargs)
            self._logger = logging.getLogger(f"{cls.__module__}.{cls.__name__}")
        
        def __getattr__(self, name):
            attr = getattr(self._wrapped, name)
            if callable(attr):
                def logged_method(*args, **kwargs):
                    self._logger.debug(f"Calling {name} with args={args}, kwargs={kwargs}")
                    try:
                        result = attr(*args, **kwargs)
                        self._logger.debug(f"Method {name} completed successfully")
                        return result
                    except Exception as e:
                        self._logger.error(f"Method {name} failed: {e}")
                        raise
                return logged_method
            return attr
    
    return Wrapper


# Global log manager instance
_log_manager: Optional[LogManager] = None


def initialize_logging(config=None) -> LogManager:
    """Initialize the global logging system."""
    global _log_manager
    _log_manager = LogManager(config)
    return _log_manager


def get_log_manager() -> Optional[LogManager]:
    """Get the global log manager instance."""
    return _log_manager
