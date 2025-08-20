"""
Modern CSS styles for MongoDB Visualizer application.

This module provides a comprehensive set of modern, engaging styles
that follow Material Design principles and contemporary UI/UX standards.
"""

class ModernStyles:
    """Collection of modern CSS styles for the MongoDB Visualizer application."""
    
    # Color scheme
    COLORS = {
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
    }
    
    @classmethod
    def get_main_window_style(cls):
        """Get the main window stylesheet."""
        return f"""
        QMainWindow {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 14px;
        }}
        
        QMainWindow::separator {{
            background: {cls.COLORS['border']};
            width: 2px;
            height: 2px;
        }}
        
        QMainWindow::separator:hover {{
            background: {cls.COLORS['primary']};
        }}
        
        QWidget {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
        }}
        
        /* Improve spacing for main layout */
        QVBoxLayout {{
            spacing: 8px;
            margin: 8px;
        }}
        
        QHBoxLayout {{
            spacing: 8px;
            margin: 4px;
        }}
        """
    
    @classmethod
    def get_menu_bar_style(cls):
        """Get the menu bar stylesheet."""
        return f"""
        QMenuBar {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: none;
            font-weight: 500;
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 8px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {cls.COLORS['hover']};
            color: {cls.COLORS['primary']};
        }}
        
        QMenuBar::item:pressed {{
            background-color: {cls.COLORS['primary_light']};
            color: white;
        }}
        
        QMenu {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: 8px 0px;
        }}
        
        QMenu::item {{
            padding: 8px 20px;
            margin: 2px 8px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {cls.COLORS['hover']};
            color: {cls.COLORS['primary']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {cls.COLORS['border']};
            margin: 8px 16px;
        }}
        """
    
    @classmethod
    def get_tool_bar_style(cls):
        """Get the toolbar stylesheet."""
        return f"""
        QToolBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
            border: none;
            border-bottom: 2px solid {cls.COLORS['border']};
            padding: 12px 16px;
            spacing: 12px;
            min-height: 50px;
            font-weight: 600;
        }}
        
        QToolBar::separator {{
            background-color: {cls.COLORS['border_dark']};
            width: 2px;
            margin: 8px 12px;
            border-radius: 1px;
        }}
        
        QToolButton {{
            background: transparent;
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 10px 16px;
            margin: 4px;
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            font-size: 14px;
            min-height: 28px;
            min-width: 80px;
            text-align: center;
        }}
        
        QToolButton:hover {{
            background-color: {cls.COLORS['hover']};
            border-color: {cls.COLORS['primary_light']};
            color: {cls.COLORS['primary']};
        }}
        
        QToolButton:pressed {{
            background-color: {cls.COLORS['primary_light']};
            color: white;
        }}
        
        QToolButton:checked {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border-color: {cls.COLORS['primary_dark']};
        }}
        """
    
    @classmethod
    def get_status_bar_style(cls):
        """Get the status bar stylesheet."""
        return f"""
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_secondary']};
            border: none;
            border-top: 1px solid {cls.COLORS['border']};
            padding: 4px 8px;
            font-size: 12px;
        }}
        
        QStatusBar::item {{
            border: none;
        }}
        
        QLabel {{
            color: {cls.COLORS['text_secondary']};
            padding: 0px;
            border: none;
            background: transparent;
        }}
        
        QProgressBar {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 6px;
            background-color: {cls.COLORS['background']};
            text-align: center;
            font-weight: bold;
            height: 16px;
        }}
        
        QProgressBar::chunk {{
            background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 {cls.COLORS['primary']}, 
                stop: 1 {cls.COLORS['primary_light']});
            border-radius: 5px;
        }}
        """
    
    @classmethod
    def get_tree_widget_style(cls):
        """Get the tree widget stylesheet."""
        return f"""
        QTreeWidget {{
            background-color: {cls.COLORS['surface']};
            alternate-background-color: #fafafa;
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            outline: none;
            font-size: 14px;
            font-weight: 500;
            gridline-color: {cls.COLORS['border']};
            padding: 4px;
        }}
        
        QTreeWidget::item {{
            padding: 10px 15px;
            border: none;
            border-bottom: 1px solid transparent;
            min-height: 28px;
            color: {cls.COLORS['text_primary']};
            font-weight: 500;
        }}
        
        QTreeWidget::item:hover {{
            background-color: {cls.COLORS['hover']};
            border-radius: 6px;
            margin: 1px;
            color: {cls.COLORS['primary']};
            font-weight: 600;
        }}
        
        QTreeWidget::item:selected {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border-radius: 6px;
            margin: 1px;
            font-weight: 600;
        }}
        
        QTreeWidget::item:selected:!active {{
            background-color: {cls.COLORS['primary_light']};
            color: white;
            font-weight: 600;
        }}
        
        QTreeWidget::branch {{
            background-color: transparent;
        }}
        
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: url(none);
        }}
        
        QTreeWidget::branch:has-siblings:adjoins-item {{
            border-image: url(none);
        }}
        
        QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(none);
        }}
        
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTYgNCAxMiA4IDYgMTJWNFoiIGZpbGw9IiM3NTc1NzUiLz4KPC9zdmc+);
        }}
        
        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNiA4IDEyIDEyIDZINFoiIGZpbGw9IiM3NTc1NzUiLz4KPC9zdmc+);
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['primary']};
            color: white;
            padding: 12px 15px;
            border: none;
            border-bottom: 2px solid {cls.COLORS['primary_dark']};
            font-weight: 600;
            font-size: 14px;
        }}
        """
    
    @classmethod
    def get_button_style(cls):
        """Get button stylesheet."""
        return f"""
        QPushButton {{
            background-color: {cls.COLORS['primary']};
            color: white !important;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
            min-height: 16px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS['primary_light']};
            color: white !important;
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS['primary_dark']};
            color: white !important;
        }}
        
        QPushButton:disabled {{
            background-color: {cls.COLORS['text_disabled']};
            color: white !important;
        }}
        
        QPushButton.secondary {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['primary']} !important;
            border: 2px solid {cls.COLORS['primary']};
        }}
        
        QPushButton.secondary:hover {{
            background-color: {cls.COLORS['hover']};
            color: {cls.COLORS['primary']} !important;
        }}
        
        QPushButton.secondary:pressed {{
            background-color: {cls.COLORS['primary']};
            color: white !important;
        }}
        
        QPushButton.success {{
            background-color: {cls.COLORS['success']};
        }}
        
        QPushButton.success:hover {{
            background-color: #66bb6a;
        }}
        
        QPushButton.warning {{
            background-color: {cls.COLORS['warning']};
        }}
        
        QPushButton.warning:hover {{
            background-color: #ffb74d;
        }}
        
        QPushButton.error {{
            background-color: {cls.COLORS['error']};
        }}
        
        QPushButton.error:hover {{
            background-color: #ef5350;
        }}
        """
    
    @classmethod
    def get_enhanced_button_styles(cls):
        """Get enhanced button styles for specific button types."""
        return f"""
        /* Enhanced Connect Button */
        QPushButton[objectName="connect_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4caf50, stop:1 #2e7d32) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
            min-width: 100px;
        }}
        
        QPushButton[objectName="connect_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #66bb6a, stop:1 #388e3c) !important;
            color: white !important;
        }}
        
        QPushButton[objectName="connect_button"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2e7d32, stop:1 #1b5e20) !important;
            color: white !important;
        }}
        
        /* Enhanced Disconnect Button */
        QPushButton[objectName="disconnect_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f44336, stop:1 #c62828) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
            min-width: 100px;
        }}
        
        QPushButton[objectName="disconnect_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ef5350, stop:1 #d32f2f) !important;
            color: white !important;
        }}
        
        QPushButton[objectName="disconnect_button"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #c62828, stop:1 #b71c1c) !important;
            color: white !important;
        }}
        
        /* Enhanced Refresh Button */
        QPushButton[objectName="refresh_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2196f3, stop:1 #1565c0) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
            min-width: 100px;
        }}
        
        QPushButton[objectName="refresh_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #42a5f5, stop:1 #1976d2) !important;
            color: white !important;
        }}
        
        QPushButton[objectName="refresh_button"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1565c0, stop:1 #0d47a1) !important;
            color: white !important;
        }}
        
        /* Enhanced Export Button */
        QPushButton[objectName="export_button"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff9800, stop:1 #ef6c00) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
            min-width: 100px;
        }}
        
        QPushButton[objectName="export_button"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffb74d, stop:1 #f57c00) !important;
            color: white !important;
        }}
        
        QPushButton[objectName="export_button"]:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ef6c00, stop:1 #e65100) !important;
            color: white !important;
        }}
        
        /* Toolbar Action Styling */
        QToolBar QToolButton {{
            background: transparent;
            border: 2px solid transparent;
            border-radius: 8px;
            padding: 8px 16px;
            margin: 2px;
            color: {cls.COLORS['text_primary']};
            font-weight: 600;
            font-size: 14px;
            min-height: 24px;
            min-width: 80px;
        }}
        
        QToolBar QToolButton[text="Connect"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4caf50, stop:1 #2e7d32);
            color: white;
            border: none;
        }}
        
        QToolBar QToolButton[text="Connect"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #66bb6a, stop:1 #388e3c);
        }}
        
        QToolBar QToolButton[text="Disconnect"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #f44336, stop:1 #c62828);
            color: white;
            border: none;
        }}
        
        QToolBar QToolButton[text="Disconnect"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ef5350, stop:1 #d32f2f);
        }}
        
        QToolBar QToolButton[text="Refresh"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2196f3, stop:1 #1565c0);
            color: white;
            border: none;
        }}
        
        QToolBar QToolButton[text="Refresh"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #42a5f5, stop:1 #1976d2);
        }}
        
        QToolBar QToolButton[text="Export"] {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff9800, stop:1 #ef6c00);
            color: white;
            border: none;
        }}
        
        QToolBar QToolButton[text="Export"]:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffb74d, stop:1 #f57c00);
        }}
        
        QToolBar QToolButton:pressed {{
        }}
        """
    
    @classmethod
    def get_input_style(cls):
        """Get input field stylesheet."""
        return f"""
        QLineEdit {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 2px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            min-height: 20px;
            selection-background-color: {cls.COLORS['primary_light']};
        }}
        
        QLineEdit:focus {{
            border-color: {cls.COLORS['primary']};
            background-color: white;
        }}
        
        QLineEdit:disabled {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_disabled']};
            border-color: {cls.COLORS['text_disabled']};
        }}
        
        QTextEdit {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 2px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: 16px;
            font-size: 14px;
            line-height: 1.4;
            selection-background-color: {cls.COLORS['primary_light']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        
        QTextEdit:focus {{
            border-color: {cls.COLORS['primary']};
            background-color: white;
        }}
        
        QTextEdit:disabled {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_disabled']};
            border-color: {cls.COLORS['text_disabled']};
        }}
        
        QComboBox {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 2px solid {cls.COLORS['border']};
            border-radius: 6px;
            padding-left: 15px;
            font-size: 13px;
            min-height: 14px;
            max-height: 20px;
            selection-background-color: {cls.COLORS['hover']};
            combobox-popup: 0;
        }}
        
        QComboBox:focus {{
            border-color: {cls.COLORS['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
        }}
        
        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQgNiA4IDEwIDEyIDZINFoiIGZpbGw9IiM3NTc1NzUiLz4KPC9zdmc+);
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            outline: 0px;
            selection-color: {cls.COLORS['primary']};
            selection-background-color: {cls.COLORS['hover']};
        }}
        
        QSpinBox {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border: 2px solid {cls.COLORS['border']};
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 13px;
            min-height: 14px;
            max-height: 15px;
            min-width: 80px;
        }}
        
        QSpinBox:focus {{
            border-color: {cls.COLORS['primary']};
        }}
        
        QSpinBox::up-button {{
            background-color: {cls.COLORS['background']};
            border: none;
            border-left: 1px solid {cls.COLORS['border']};
            border-top-right-radius: 6px;
            width: 20px;
        }}
        
        QSpinBox::down-button {{
            background-color: {cls.COLORS['background']};
            border: none;
            border-left: 1px solid {cls.COLORS['border']};
            border-bottom-right-radius: 6px;
            width: 20px;
        }}
        """
    
    @classmethod
    def get_dialog_style(cls):
        """Get dialog stylesheet."""
        return f"""
        QDialog {{
            background-color: {cls.COLORS['surface']};
            color: {cls.COLORS['text_primary']};
            border-radius: 12px;
        }}
        
        QGroupBox {{
            background-color: {cls.COLORS['surface']};
            border: 2px solid {cls.COLORS['border']};
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 20px;
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 4px 12px;
            color: {cls.COLORS['primary']};
            font-weight: bold;
            background-color: {cls.COLORS['surface']};
            border-radius: 4px;
            margin-top: -8px;
        }}
        
        QLabel {{
            color: {cls.COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
            padding: 0px;
            border: none;
            background: transparent;
        }}
        
        QLabel[class="header"] {{
            font-size: 18px;
            font-weight: 700;
            color: {cls.COLORS['primary']};
            padding: 8px 0px;
        }}
        
        QLabel[class="subtitle"] {{
            font-size: 12px;
            color: {cls.COLORS['text_secondary']};
            font-weight: 400;
        }}
        
        QLabel[class="field-label"] {{
            font-weight: 600;
            color: {cls.COLORS['text_primary']};
            margin-bottom: 4px;
        }}
        
        QFrame {{
            border-radius: 8px;
        }}
        """
    
    @classmethod
    def get_table_style(cls):
        """Get table widget stylesheet."""
        return f"""
        QTableWidget {{
            background-color: {cls.COLORS['surface']};
            alternate-background-color: #fafafa;
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            gridline-color: {cls.COLORS['border']};
            outline: none;
            font-size: 14px;
        }}
        
        QTableWidget::item {{
            padding: 8px 12px;
            border: none;
        }}
        
        QTableWidget::item:hover {{
            background-color: {cls.COLORS['hover']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {cls.COLORS['primary_light']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
            padding: 12px 16px;
            border: none;
            border-bottom: 2px solid {cls.COLORS['primary']};
            font-weight: 600;
            font-size: 14px;
        }}
        
        QHeaderView::section:hover {{
            background-color: {cls.COLORS['hover']};
        }}
        """
    
    @classmethod
    def get_tab_widget_style(cls):
        """Get tab widget stylesheet."""
        return f"""
        QTabWidget::pane {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            margin-top: -1px;
            padding: 8px;
        }}
        
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text_primary']};
            border: 1px solid {cls.COLORS['border']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 12px 24px;
            margin-right: 4px;
            font-weight: 600;
            font-size: 14px;
            min-width: 100px;
            min-height: 24px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border-color: {cls.COLORS['primary']};
            font-weight: 700;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {cls.COLORS['hover']};
            color: {cls.COLORS['primary']};
            border-color: {cls.COLORS['primary_light']};
        }}
        
        QTabBar::tab:first {{
            margin-left: 0;
        }}
        """
    
    @classmethod
    def get_splitter_style(cls):
        """Get splitter stylesheet."""
        return f"""
        QSplitter::handle {{
            background-color: transparent;
            border: none;
            width: 0px;
            height: 0px;
        }}
        
        QSplitter::handle:horizontal {{
            width: 0px;
            margin: 0px;
        }}
        
        QSplitter::handle:vertical {{
            height: 0px;
            margin: 0px;
        }}
        
        QSplitter::handle:hover {{
            background-color: transparent;
        }}
        
        QSplitter::handle:pressed {{
            background-color: transparent;
        }}
        
        QSplitter {{
            border: none;
        }}
        """
    
    @classmethod
    def get_scroll_bar_style(cls):
        """Get scrollbar stylesheet."""
        return f"""
        QScrollBar:vertical {{
            background-color: {cls.COLORS['background']};
            width: 12px;
            border-radius: 6px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['text_disabled']};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['text_secondary']};
        }}
        
        QScrollBar::handle:vertical:pressed {{
            background-color: {cls.COLORS['primary']};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        QScrollBar:horizontal {{
            background-color: {cls.COLORS['background']};
            height: 12px;
            border-radius: 6px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {cls.COLORS['text_disabled']};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {cls.COLORS['text_secondary']};
        }}
        
        QScrollBar::handle:horizontal:pressed {{
            background-color: {cls.COLORS['primary']};
        }}
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}
        """
    
    @classmethod
    def get_card_style(cls):
        """Get card style for document containers."""
        return f"""
        .document-card {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 12px;
            margin: 8px 0px;
            padding: 16px;
        }}
        
        .document-card:hover {{
            border-color: {cls.COLORS['primary_light']};
            transform: translateY(-2px);
        }}
        
        .card-header {{
            background-color: {cls.COLORS['background']};
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 12px;
            border-left: 4px solid {cls.COLORS['primary']};
        }}
        
        .card-actions {{
            background-color: {cls.COLORS['background']};
            border-radius: 8px;
            padding: 8px;
            margin-top: 12px;
        }}
        """
    
    @classmethod
    def get_complete_stylesheet(cls):
        """Get the complete application stylesheet."""
        return f"""
        {cls.get_main_window_style()}
        {cls.get_menu_bar_style()}
        {cls.get_tool_bar_style()}
        {cls.get_status_bar_style()}
        {cls.get_tree_widget_style()}
        {cls.get_button_style()}
        {cls.get_enhanced_button_styles()}
        {cls.get_input_style()}
        {cls.get_dialog_style()}
        {cls.get_table_style()}
        {cls.get_tab_widget_style()}
        {cls.get_splitter_style()}
        {cls.get_scroll_bar_style()}
        
        /* Tooltips */
        QToolTip {{
            background-color: {cls.COLORS['on_surface']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 12px;
            opacity: 0.9;
        }}
        
        /* Selection */
        ::selection {{
            background-color: {cls.COLORS['primary_light']};
            color: white;
        }}
        """
