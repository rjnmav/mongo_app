"""
Utility functions and helpers for the MongoDB Visualizer application.

This module provides various utility functions, formatters, validators,
and helper classes used throughout the application.
"""

import json
import re
import hashlib
import platform
import psutil
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timezone
from pathlib import Path
import logging

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtGui import QFont, QFontMetrics


def format_bytes(bytes_count: int) -> str:
    """
    Format bytes to human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if bytes_count == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = abs(bytes_count)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_number(number: Union[int, float]) -> str:
    """
    Format large numbers with thousand separators.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted string with commas
    """
    if isinstance(number, float):
        if number.is_integer():
            return f"{int(number):,}"
        else:
            return f"{number:,.2f}"
    return f"{number:,}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with suffix.
    
    Args:
        text: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def validate_json(json_string: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """
    Validate JSON string and return parsed object.
    
    Args:
        json_string: JSON string to validate
        
    Returns:
        Tuple of (is_valid, parsed_object, error_message)
    """
    if not json_string.strip():
        return True, {}, None
    
    try:
        parsed = json.loads(json_string)
        return True, parsed, None
    except json.JSONDecodeError as e:
        return False, None, str(e)


def validate_mongodb_query(query: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate MongoDB query structure.
    
    Args:
        query: MongoDB query dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Basic validation - ensure it's a dictionary
        if not isinstance(query, dict):
            return False, "Query must be a dictionary"
        
        # Check for common MongoDB operators
        valid_operators = {
            '$eq', '$ne', '$gt', '$gte', '$lt', '$lte', '$in', '$nin',
            '$and', '$or', '$not', '$nor', '$exists', '$type', '$regex',
            '$where', '$all', '$elemMatch', '$size', '$mod', '$text',
            '$search', '$language', '$caseSensitive', '$diacriticSensitive'
        }
        
        def validate_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.startswith('$') and key not in valid_operators:
                        return False, f"Unknown operator: {key}"
                    if not validate_recursive(value)[0]:
                        return validate_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    if not validate_recursive(item)[0]:
                        return validate_recursive(item)
            return True, None
        
        return validate_recursive(query)
        
    except Exception as e:
        return False, f"Query validation error: {str(e)}"


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        HTML-escaped text
    """
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename


class ColorGenerator:
    """Generate consistent colors for data visualization."""
    
    def __init__(self):
        self.colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        self.index = 0
    
    def next_color(self) -> str:
        """Get next color in the sequence."""
        color = self.colors[self.index % len(self.colors)]
        self.index += 1
        return color
    
    def reset(self) -> None:
        """Reset color index to start."""
        self.index = 0
    
    def get_color_for_string(self, text: str) -> str:
        """Get consistent color for a string based on hash."""
        hash_value = hashlib.md5(text.encode()).hexdigest()
        index = int(hash_value[:8], 16) % len(self.colors)
        return self.colors[index]


class FontHelper:
    """Helper class for font management."""
    
    @staticmethod
    def get_monospace_font(size: int = 10) -> QFont:
        """Get a monospace font for code display."""
        font_families = [
            "Consolas", "Monaco", "Menlo", "Ubuntu Mono",
            "Courier New", "monospace"
        ]
        
        for family in font_families:
            font = QFont(family, size)
            font.setFixedPitch(True)
            if QFontMetrics(font).horizontalAdvance('i') == QFontMetrics(font).horizontalAdvance('w'):
                return font
        
        # Fallback to system monospace font
        font = QFont("monospace", size)
        font.setFixedPitch(True)
        return font
    
    @staticmethod
    def get_text_width(text: str, font: QFont) -> int:
        """Get pixel width of text with given font."""
        metrics = QFontMetrics(font)
        return metrics.horizontalAdvance(text)


class SystemInfo:
    """System information utilities."""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').total if platform.system() != 'Windows' else psutil.disk_usage('C:').total
        }
    
    @staticmethod
    def get_memory_usage() -> Dict[str, int]:
        """Get current memory usage."""
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'percent': memory.percent
        }
    
    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """Get current process information."""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'pid': process.pid,
            'cpu_percent': process.cpu_percent(),
            'memory_rss': memory_info.rss,
            'memory_vms': memory_info.vms,
            'num_threads': process.num_threads(),
            'create_time': datetime.fromtimestamp(process.create_time())
        }


class SettingsManager:
    """Application settings management."""
    
    def __init__(self, organization: str = "MongoDBVisualizer", application: str = "Settings"):
        self.settings = QSettings(organization, application)
    
    def save_window_geometry(self, widget: QWidget) -> None:
        """Save window geometry."""
        self.settings.setValue("geometry", widget.saveGeometry())
        self.settings.setValue("windowState", widget.saveState() if hasattr(widget, 'saveState') else None)
    
    def restore_window_geometry(self, widget: QWidget) -> None:
        """Restore window geometry."""
        geometry = self.settings.value("geometry")
        if geometry:
            widget.restoreGeometry(geometry)
        
        window_state = self.settings.value("windowState")
        if window_state and hasattr(widget, 'restoreState'):
            widget.restoreState(window_state)
    
    def save_splitter_state(self, splitter, name: str) -> None:
        """Save splitter state."""
        self.settings.setValue(f"splitter_{name}", splitter.saveState())
    
    def restore_splitter_state(self, splitter, name: str) -> None:
        """Restore splitter state."""
        state = self.settings.value(f"splitter_{name}")
        if state:
            splitter.restoreState(state)
    
    def save_value(self, key: str, value: Any) -> None:
        """Save a value to settings."""
        self.settings.setValue(key, value)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a value from settings with proper type conversion."""
        value = self.settings.value(key, default)
        
        # QSettings returns strings by default, convert based on default type
        if default is not None and isinstance(value, str):
            if isinstance(default, bool):
                # Convert string to boolean
                return value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(default, int):
                try:
                    return int(value)
                except ValueError:
                    return default
            elif isinstance(default, float):
                try:
                    return float(value)
                except ValueError:
                    return default
        
        return value
    
    def sync(self) -> None:
        """Sync settings to storage."""
        self.settings.sync()


def show_error_message(parent: QWidget, title: str, message: str, details: str = None) -> None:
    """
    Show an error message dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Main error message
        details: Optional detailed error information
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.exec_()


def show_info_message(parent: QWidget, title: str, message: str) -> None:
    """
    Show an information message dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Information message
    """
    QMessageBox.information(parent, title, message)


def show_warning_message(parent: QWidget, title: str, message: str) -> bool:
    """
    Show a warning message dialog with Yes/No buttons.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Warning message
        
    Returns:
        True if user clicked Yes, False otherwise
    """
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    return reply == QMessageBox.Yes


class JsonFormatter:
    """JSON formatting utilities."""
    
    @staticmethod
    def format_json(data: Any, indent: int = 2, sort_keys: bool = True) -> str:
        """
        Format data as pretty JSON.
        
        Args:
            data: Data to format
            indent: Indentation level
            sort_keys: Whether to sort dictionary keys
            
        Returns:
            Formatted JSON string
        """
        return json.dumps(
            data,
            indent=indent,
            sort_keys=sort_keys,
            default=str,
            ensure_ascii=False
        )
    
    @staticmethod
    def minify_json(json_string: str) -> str:
        """
        Minify JSON string by removing whitespace.
        
        Args:
            json_string: JSON string to minify
            
        Returns:
            Minified JSON string
        """
        try:
            data = json.loads(json_string)
            return json.dumps(data, separators=(',', ':'), default=str)
        except json.JSONDecodeError:
            return json_string
    
    @staticmethod
    def validate_and_format(json_string: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate and format JSON string.
        
        Args:
            json_string: JSON string to process
            
        Returns:
            Tuple of (is_valid, formatted_json, error_message)
        """
        try:
            data = json.loads(json_string)
            formatted = JsonFormatter.format_json(data)
            return True, formatted, None
        except json.JSONDecodeError as e:
            return False, json_string, str(e)


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename with timestamp.
    
    Args:
        original_path: Original file path
        
    Returns:
        Backup filename with timestamp
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(path.parent / f"{path.stem}_backup_{timestamp}{path.suffix}")


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {directory_path}: {e}")
        return False
