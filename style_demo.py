#!/usr/bin/env python3
"""
Style demonstration script for MongoDB Visualizer.

This script creates a demo window showcasing all the modern styling features
without requiring a MongoDB connection.
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QSpinBox, QCheckBox, QGroupBox, QFormLayout, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QFrame, QProgressBar, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import qtawesome as qta

from src.styles.theme_manager import theme_manager, ThemeType
from src.styles.modern_styles import ModernStyles


class StyleDemoWindow(QMainWindow):
    """Demonstration window for modern styles."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the demo UI."""
        self.setWindowTitle("MongoDB Visualizer - Modern Style Demo")
        self.setMinimumSize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Add tabs
        self.create_components_tab(tab_widget)
        self.create_forms_tab(tab_widget)
        self.create_data_tab(tab_widget)
        self.create_themes_tab(tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready - MongoDB Visualizer Style Demo")
        
        # Apply initial theme
        theme_manager.apply_initial_theme()
    
    def create_components_tab(self, parent):
        """Create the components demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("UI Components Showcase")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 16px; color: " + 
                           ModernStyles.COLORS['primary'])
        layout.addWidget(header)
        
        # Buttons section
        buttons_group = QGroupBox("Buttons")
        buttons_layout = QHBoxLayout(buttons_group)
        
        primary_btn = QPushButton("Primary Button")
        primary_btn.setObjectName("primary")
        buttons_layout.addWidget(primary_btn)
        
        secondary_btn = QPushButton("Secondary Button")
        secondary_btn.setProperty("class", "secondary")
        buttons_layout.addWidget(secondary_btn)
        
        success_btn = QPushButton("Success Button")
        success_btn.setProperty("class", "success")
        buttons_layout.addWidget(success_btn)
        
        warning_btn = QPushButton("Warning Button")
        warning_btn.setProperty("class", "warning")
        buttons_layout.addWidget(warning_btn)
        
        error_btn = QPushButton("Error Button")
        error_btn.setProperty("class", "error")
        buttons_layout.addWidget(error_btn)
        
        layout.addWidget(buttons_group)
        
        # Progress and status
        progress_group = QGroupBox("Progress & Status")
        progress_layout = QVBoxLayout(progress_group)
        
        progress_bar = QProgressBar()
        progress_bar.setValue(65)
        progress_layout.addWidget(QLabel("Loading progress:"))
        progress_layout.addWidget(progress_bar)
        
        layout.addWidget(progress_group)
        
        # Cards demo
        cards_group = QGroupBox("Card Components")
        cards_layout = QVBoxLayout(cards_group)
        
        card1 = QFrame()
        card1.setStyleSheet(f"""
            QFrame {{
                background-color: {ModernStyles.COLORS['surface']};
                border: 1px solid {ModernStyles.COLORS['border']};
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0px;
            }}
            QFrame:hover {{
                border-color: {ModernStyles.COLORS['primary']};
                box-shadow: 0 4px 12px {ModernStyles.COLORS['shadow']};
            }}
        """)
        card1_layout = QVBoxLayout(card1)
        card1_layout.addWidget(QLabel("Sample Document Card"))
        card1_layout.addWidget(QLabel("This demonstrates how documents appear in the viewer"))
        cards_layout.addWidget(card1)
        
        layout.addWidget(cards_group)
        
        layout.addStretch()
        parent.addTab(widget, "Components")
    
    def create_forms_tab(self, parent):
        """Create the forms demonstration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Form Controls")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 16px; color: " + 
                           ModernStyles.COLORS['primary'])
        layout.addWidget(header)
        
        # Form group
        form_group = QGroupBox("Connection Settings")
        form_layout = QFormLayout(form_group)
        
        # Text inputs
        host_input = QLineEdit()
        host_input.setPlaceholderText("localhost")
        form_layout.addRow("Host:", host_input)
        
        port_input = QSpinBox()
        port_input.setRange(1, 65535)
        port_input.setValue(27017)
        form_layout.addRow("Port:", port_input)
        
        # Combo box
        auth_combo = QComboBox()
        auth_combo.addItems(["No Authentication", "Username/Password", "X.509 Certificate"])
        form_layout.addRow("Authentication:", auth_combo)
        
        # Checkboxes
        ssl_check = QCheckBox("Use SSL/TLS")
        form_layout.addRow("Security:", ssl_check)
        
        layout.addWidget(form_group)
        
        # Text area
        query_group = QGroupBox("Query Editor")
        query_layout = QVBoxLayout(query_group)
        
        query_text = QTextEdit()
        query_text.setPlaceholderText("Enter your MongoDB query here...")
        query_text.setMaximumHeight(150)
        query_layout.addWidget(query_text)
        
        layout.addWidget(query_group)
        
        layout.addStretch()
        parent.addTab(widget, "Forms")
    
    def create_data_tab(self, parent):
        """Create the data visualization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Data Visualization")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 16px; color: " + 
                           ModernStyles.COLORS['primary'])
        layout.addWidget(header)
        
        # Splitter with tree and table
        splitter = QSplitter(Qt.Horizontal)
        
        # Tree widget
        tree = QTreeWidget()
        tree.setHeaderLabel("Database Structure")
        
        # Add sample data
        db_item = QTreeWidgetItem(tree)
        db_item.setText(0, "sample_database")
        db_item.setIcon(0, qta.icon('fa5s.database', color=ModernStyles.COLORS['primary']))
        
        coll_item = QTreeWidgetItem(db_item)
        coll_item.setText(0, "users")
        coll_item.setIcon(0, qta.icon('fa5s.table', color=ModernStyles.COLORS['secondary']))
        
        coll_item2 = QTreeWidgetItem(db_item)
        coll_item2.setText(0, "products")
        coll_item2.setIcon(0, qta.icon('fa5s.table', color=ModernStyles.COLORS['secondary']))
        
        tree.expandAll()
        splitter.addWidget(tree)
        
        # Table widget
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Field", "Type", "Value"])
        
        # Add sample data
        sample_data = [
            ["_id", "ObjectId", "507f1f77bcf86cd799439011"],
            ["name", "String", "John Doe"],
            ["email", "String", "john@example.com"],
            ["age", "Number", "30"],
            ["active", "Boolean", "true"]
        ]
        
        for row, (field, type_val, value) in enumerate(sample_data):
            table.setItem(row, 0, QTableWidgetItem(field))
            table.setItem(row, 1, QTableWidgetItem(type_val))
            table.setItem(row, 2, QTableWidgetItem(value))
        
        table.resizeColumnsToContents()
        splitter.addWidget(table)
        
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        parent.addTab(widget, "Data")
    
    def create_themes_tab(self, parent):
        """Create the themes tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel("Theme Selection")
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 16px; color: " + 
                           ModernStyles.COLORS['primary'])
        layout.addWidget(header)
        
        # Theme buttons
        themes_group = QGroupBox("Available Themes")
        themes_layout = QVBoxLayout(themes_group)
        
        for theme in ThemeType:
            btn = QPushButton(f"{theme.value.title()} Theme")
            btn.clicked.connect(lambda checked, t=theme: self.change_theme(t))
            themes_layout.addWidget(btn)
        
        layout.addWidget(themes_group)
        
        # Theme info
        info_group = QGroupBox("Theme Information")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
        <h3>Modern Styling Features:</h3>
        <ul>
        <li><b>Material Design Inspired:</b> Clean, modern interface following Material Design principles</li>
        <li><b>Multiple Themes:</b> Light, Dark, Blue, and Green themes</li>
        <li><b>Responsive Design:</b> Hover effects and smooth transitions</li>
        <li><b>Professional Colors:</b> Carefully selected color palettes</li>
        <li><b>Enhanced Typography:</b> Improved fonts and text hierarchy</li>
        <li><b>Card-based Layout:</b> Modern card components for better organization</li>
        <li><b>Consistent Styling:</b> Unified design across all components</li>
        </ul>
        """)
        info_text.setWordWrap(True)
        info_text.setTextFormat(Qt.RichText)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        parent.addTab(widget, "Themes")
    
    def change_theme(self, theme: ThemeType):
        """Change the application theme."""
        theme_manager.set_theme(theme)
        self.statusBar().showMessage(f"Theme changed to: {theme.value.title()}")


def main():
    """Run the style demo application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create and show the demo window
    demo = StyleDemoWindow()
    demo.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
