"""
Theme manager for MongoDB Visualizer application.

Provides functionality to switch between different themes and manage
application-wide styling.
"""

from enum import Enum
from typing import Dict, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from .modern_styles import ModernStyles

class ThemeType(Enum):
    """Available theme types."""
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"

class ThemeManager(QObject):
    """Manages application themes and styling."""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = ThemeType.LIGHT
        self.themes = self._initialize_themes()
    
    def _initialize_themes(self) -> Dict[ThemeType, Dict[str, str]]:
        """Initialize all available themes."""
        return {
            ThemeType.LIGHT: {
                'primary': '#1976d2',
                'primary_light': '#42a5f5',
                'primary_dark': '#1565c0',
                'secondary': '#dc004e',
                'secondary_light': '#ff5983',
                'secondary_dark': '#9a0036',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
                'info': '#2196f3',
                'background': '#f5f5f5',
                'surface': '#ffffff',
                'on_background': '#212121',
                'on_surface': '#212121',
                'border': '#e0e0e0',
                'border_dark': '#bdbdbd',
                'text_primary': '#212121',
                'text_secondary': '#757575',
                'text_disabled': '#bdbdbd',
                'hover': '#e3f2fd',
                'selection': '#1976d2',
                'shadow': 'rgba(0, 0, 0, 0.1)'
            },
            ThemeType.DARK: {
                'primary': '#bb86fc',
                'primary_light': '#d7b3ff',
                'primary_dark': '#9965f4',
                'secondary': '#03dac6',
                'secondary_light': '#66fff9',
                'secondary_dark': '#00a896',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#cf6679',
                'info': '#2196f3',
                'background': '#121212',
                'surface': '#1e1e1e',
                'on_background': '#ffffff',
                'on_surface': '#ffffff',
                'border': '#333333',
                'border_dark': '#555555',
                'text_primary': '#ffffff',
                'text_secondary': '#b3b3b3',
                'text_disabled': '#666666',
                'hover': '#2d2d2d',
                'selection': '#bb86fc',
                'shadow': 'rgba(0, 0, 0, 0.3)'
            },
            ThemeType.BLUE: {
                'primary': '#0d47a1',
                'primary_light': '#5472d3',
                'primary_dark': '#002171',
                'secondary': '#ff6f00',
                'secondary_light': '#ff9f40',
                'secondary_dark': '#c43e00',
                'success': '#2e7d32',
                'warning': '#f57c00',
                'error': '#c62828',
                'info': '#1565c0',
                'background': '#f3f7fd',
                'surface': '#ffffff',
                'on_background': '#212121',
                'on_surface': '#212121',
                'border': '#bbdefb',
                'border_dark': '#90caf9',
                'text_primary': '#212121',
                'text_secondary': '#757575',
                'text_disabled': '#bdbdbd',
                'hover': '#e1f5fe',
                'selection': '#0d47a1',
                'shadow': 'rgba(13, 71, 161, 0.1)'
            },
            ThemeType.GREEN: {
                'primary': '#2e7d32',
                'primary_light': '#60ad5e',
                'primary_dark': '#005005',
                'secondary': '#e65100',
                'secondary_light': '#ff8a50',
                'secondary_dark': '#ac1900',
                'success': '#388e3c',
                'warning': '#f57c00',
                'error': '#d32f2f',
                'info': '#1976d2',
                'background': '#f1f8e9',
                'surface': '#ffffff',
                'on_background': '#212121',
                'on_surface': '#212121',
                'border': '#c8e6c9',
                'border_dark': '#a5d6a7',
                'text_primary': '#212121',
                'text_secondary': '#757575',
                'text_disabled': '#bdbdbd',
                'hover': '#e8f5e8',
                'selection': '#2e7d32',
                'shadow': 'rgba(46, 125, 50, 0.1)'
            }
        }
    
    def get_current_theme(self) -> ThemeType:
        """Get the current theme."""
        return self.current_theme
    
    def set_theme(self, theme: ThemeType):
        """Set the application theme."""
        if theme in self.themes:
            self.current_theme = theme
            self._apply_theme()
            self.theme_changed.emit(theme.value)
    
    def _apply_theme(self):
        """Apply the current theme to the application."""
        colors = self.themes[self.current_theme]
        
        # Update ModernStyles colors
        ModernStyles.COLORS.update(colors)
        
        # Apply to QApplication
        app = QApplication.instance()
        if app:
            stylesheet = ModernStyles.get_complete_stylesheet()
            app.setStyleSheet(stylesheet)
    
    def get_theme_names(self) -> list:
        """Get list of available theme names."""
        return [theme.value for theme in ThemeType]
    
    def apply_initial_theme(self):
        """Apply the initial theme on startup."""
        self._apply_theme()
    
    def refresh_styles(self):
        """Refresh and reapply current styles."""
        self._apply_theme()
    
    def get_color(self, color_name: str) -> str:
        """Get a specific color from the current theme."""
        return self.themes[self.current_theme].get(color_name, '#000000')

# Global theme manager instance
theme_manager = ThemeManager()
