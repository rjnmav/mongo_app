"""
Style utilities for MongoDB Visualizer application.

Provides helper functions for applying consistent styling
across different components.
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QWidget
from .modern_styles import ModernStyles

class StyleUtils:
    """Utility class for consistent styling."""
    
    @staticmethod
    def apply_card_style(widget: QWidget, elevated: bool = True) -> None:
        """Apply card styling to a widget."""
        shadow = "0 4px 12px " + ModernStyles.COLORS['shadow'] if elevated else "0 1px 3px " + ModernStyles.COLORS['shadow']
        
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernStyles.COLORS['surface']};
                border: 1px solid {ModernStyles.COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                margin: 8px;
            }}
            QWidget:hover {{
                border-color: {ModernStyles.COLORS['primary_light']};
                box-shadow: {shadow};
            }}
        """)
    
    @staticmethod
    def apply_header_style(widget: QWidget, size: str = "medium") -> None:
        """Apply header styling to a widget."""
        sizes = {
            "small": "16px",
            "medium": "20px",
            "large": "24px"
        }
        
        font_size = sizes.get(size, "20px")
        
        widget.setStyleSheet(f"""
            QLabel {{
                font-size: {font_size};
                font-weight: 700;
                color: {ModernStyles.COLORS['primary']};
                padding: 12px 16px;
                background-color: {ModernStyles.COLORS['background']};
                border-radius: 8px;
                margin-bottom: 8px;
            }}
        """)
    
    @staticmethod
    def apply_field_label_style(widget: QWidget) -> None:
        """Apply field label styling."""
        widget.setStyleSheet(f"""
            QLabel {{
                font-weight: 600;
                color: {ModernStyles.COLORS['text_primary']};
                font-size: 14px;
                padding: 4px 0px;
                margin-bottom: 4px;
            }}
        """)
    
    @staticmethod
    def apply_value_label_style(widget: QWidget, highlight: bool = False) -> None:
        """Apply value label styling."""
        bg_color = ModernStyles.COLORS['background'] if highlight else "transparent"
        text_color = ModernStyles.COLORS['primary'] if highlight else ModernStyles.COLORS['text_secondary']
        
        widget.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 14px;
                padding: 6px 12px;
                background-color: {bg_color};
                border-radius: 4px;
                font-weight: 500;
            }}
        """)
    
    @staticmethod
    def apply_query_area_style(widget: QWidget) -> None:
        """Apply query area specific styling."""
        widget.setStyleSheet(f"""
            QGroupBox {{
                background-color: {ModernStyles.COLORS['surface']};
                border: 2px solid {ModernStyles.COLORS['border']};
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 24px;
                padding-left: 16px;
                padding-right: 16px;
                padding-bottom: 16px;
                font-weight: 600;
                color: {ModernStyles.COLORS['text_primary']};
                font-size: 16px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 8px 16px;
                color: {ModernStyles.COLORS['primary']};
                font-weight: bold;
                font-size: 16px;
                background-color: {ModernStyles.COLORS['surface']};
                border-radius: 6px;
                margin-top: -12px;
            }}
            
            QHBoxLayout {{
                spacing: 12px;
                margin: 8px 0px;
            }}
            
            QVBoxLayout {{
                spacing: 12px;
                margin: 8px 0px;
            }}
            
            QLabel {{
                font-weight: 600;
                color: {ModernStyles.COLORS['text_primary']};
                font-size: 14px;
                padding: 4px 8px;
                min-height: 20px;
            }}
            
            QLineEdit {{
                background-color: white;
                border: 2px solid {ModernStyles.COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                min-height: 24px;
                min-width: 120px;
                color: {ModernStyles.COLORS['text_primary']};
            }}
            
            QLineEdit:focus {{
                border-color: {ModernStyles.COLORS['primary']};
                box-shadow: 0 0 0 3px {ModernStyles.COLORS['primary']}33;
            }}
            
            QSpinBox {{
                background-color: white;
                border: 2px solid {ModernStyles.COLORS['border']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                min-height: 24px;
                min-width: 80px;
                color: {ModernStyles.COLORS['text_primary']};
            }}
            
            QSpinBox:focus {{
                border-color: {ModernStyles.COLORS['primary']};
                box-shadow: 0 0 0 3px {ModernStyles.COLORS['primary']}33;
            }}
            
            QPushButton {{
                min-height: 32px;
                min-width: 100px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }}
            
            QTextEdit {{
                background-color: white;
                border: 2px solid {ModernStyles.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 14px;
                line-height: 1.5;
                color: {ModernStyles.COLORS['text_primary']};
                min-height: 60px;
            }}
            
            QTextEdit:focus {{
                border-color: {ModernStyles.COLORS['primary']};
                box-shadow: 0 0 0 3px {ModernStyles.COLORS['primary']}33;
            }}
        """)
    
    @staticmethod
    def apply_button_group_style(widget: QWidget) -> None:
        """Apply styling for button groups."""
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernStyles.COLORS['background']};
                border-radius: 8px;
                padding: 8px;
                margin: 4px 0px;
            }}
            
            QPushButton {{
                margin: 2px 4px;
                min-width: 80px;
            }}
        """)
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for status indicators."""
        status_colors = {
            'success': ModernStyles.COLORS['success'],
            'warning': ModernStyles.COLORS['warning'],
            'error': ModernStyles.COLORS['error'],
            'info': ModernStyles.COLORS['info'],
            'primary': ModernStyles.COLORS['primary'],
            'default': ModernStyles.COLORS['text_secondary']
        }
        return status_colors.get(status.lower(), status_colors['default'])
    
    @staticmethod
    def apply_statistics_style(widget: QWidget) -> None:
        """Apply styling for statistics display."""
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernStyles.COLORS['surface']};
                border: 1px solid {ModernStyles.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
                margin: 8px 0px;
            }}
            
            QLabel {{
                color: {ModernStyles.COLORS['text_primary']};
                font-size: 14px;
                line-height: 1.4;
                padding: 2px 0px;
            }}
        """)
