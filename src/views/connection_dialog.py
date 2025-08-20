"""
Enhanced connection dialog for MongoDB Visualizer.

This module provides a comprehensive database connection dialog with
recent connections, connection testing, and advanced options.
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, QWidget,
    QLineEdit, QSpinBox, QCheckBox, QPushButton, QLabel, QGroupBox,
    QComboBox, QTextEdit, QProgressBar, QListWidget, QListWidgetItem,
    QSplitter, QFrame, QMessageBox, QSizePolicy, QApplication,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient
import qtawesome as qta

from ..models.data_models import ConnectionInfo, ConnectionStatus
from ..utils.helpers import show_error_message, show_info_message
from ..utils.logging_config import get_logger
from ..styles.modern_styles import ModernStyles


# CustomTitleBar class has been removed as it's no longer needed


class ConnectionTestWorker(QThread):
    """Worker thread for testing database connections."""
    
    test_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, controller, connection_info: ConnectionInfo):
        super().__init__()
        self.controller = controller
        self.connection_info = connection_info
        self.logger = get_logger(__name__)
    
    def run(self):
        """Test the database connection."""
        try:
            success = self.controller.test_connection(self.connection_info)
            if success:
                self.test_completed.emit(True, "Connection successful!")
            else:
                self.test_completed.emit(False, "Connection failed - please check your settings")
        except Exception as e:
            self.test_completed.emit(False, f"Connection error: {str(e)}")


class RecentConnectionsWidget(QWidget):
    """Widget for managing recent connections."""
    
    connection_selected = pyqtSignal(ConnectionInfo)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.logger = get_logger(__name__)
        self.init_ui()
        self.load_recent_connections()
    
    def init_ui(self):
        """Initialize the recent connections UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header
        header_label = QLabel("Recent Connections")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(16)
        header_label.setFont(header_font)
        header_label.setStyleSheet("""
            QLabel {
                color: #1976d2;
                padding: 8px 0px;
                font-size: 20px;
                font-weight: bold;
                border: none;
                background: transparent;
                margin: 0px;
            }
        """)
        layout.addWidget(header_label)
        
        # Instruction label
        instruction_label = QLabel("Click on a connection to connect immediately")
        instruction_label.setStyleSheet("""
            QLabel {
                color: #666; 
                font-size: 13px; 
                font-style: italic;
                padding: 0px 0px 8px 0px;
                border: none;
                background: transparent;
                margin: 0px;
            }
        """)
        layout.addWidget(instruction_label)
        
        # Connections list
        self.connections_list = QListWidget()
        self.connections_list.setMinimumHeight(220)
        self.connections_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                outline: none;
            }
            QListWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #f0f0f0;
                min-height: 24px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
                font-weight: 500;
                border: 1px solid #1976d2;
            }
        """)
        self.connections_list.itemDoubleClicked.connect(self.on_connection_double_clicked)
        self.connections_list.itemClicked.connect(self.on_connection_clicked)
        layout.addWidget(self.connections_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        connect_btn = QPushButton("Connect")
        connect_btn.setMinimumHeight(40)
        connect_btn.setMinimumWidth(90)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        connect_btn.clicked.connect(self.connect_selected)
        button_layout.addWidget(connect_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setMinimumHeight(40)
        remove_btn.setMinimumWidth(90)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh connections list")
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setMinimumWidth(50)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 14px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        refresh_btn.clicked.connect(self.load_recent_connections)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
    
    def load_recent_connections(self):
        """Load recent connections from the controller."""
        self.connections_list.clear()
        
        recent_connections = self.controller.get_recent_connections()
        for connection in recent_connections:
            # Create a more detailed display name
            display_name = connection.get_display_name()
            if len(display_name) > 30:  # Prevent text cutting
                display_name = display_name[:28] + "..."
            
            item = QListWidgetItem(display_name)
            item.setData(Qt.UserRole, connection)
            
            # Set item font for better readability
            font = QFont()
            font.setPointSize(14)
            font.setWeight(QFont.Medium)
            item.setFont(font)
            
            # Add detailed tooltip with connection details
            tooltip = f"Connection: {connection.name or 'Unnamed'}\n"
            tooltip += f"Host: {connection.host}:{connection.port}\n"
            if connection.auth_enabled:
                tooltip += f"Username: {connection.username}\n"
                tooltip += f"Auth DB: {connection.auth_database}"
            else:
                tooltip += "Authentication: Disabled"
            item.setToolTip(tooltip)
            
            # Set proper size hint to prevent cutting
            item.setSizeHint(item.sizeHint())
            
            self.connections_list.addItem(item)
    
    def on_connection_clicked(self, item: QListWidgetItem):
        """Handle single-click on connection item."""
        connection = item.data(Qt.UserRole)
        if connection:
            self.connection_selected.emit(connection)

    def on_connection_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on connection item."""
        connection = item.data(Qt.UserRole)
        if connection:
            self.connection_selected.emit(connection)
    
    def connect_selected(self):
        """Connect to the selected connection."""
        current_item = self.connections_list.currentItem()
        if current_item:
            connection = current_item.data(Qt.UserRole)
            if connection:
                self.connection_selected.emit(connection)
    
    def remove_selected(self):
        """Remove the selected connection from recent list."""
        current_row = self.connections_list.currentRow()
        if current_row >= 0:
            self.connections_list.takeItem(current_row)
            # TODO: Implement removal from persistent storage


class BasicConnectionWidget(QWidget):
    """Widget for basic connection settings."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the basic connection UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: white;
                border-radius: 5px;
                background: qlineargradient(y1:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        connection_layout = QFormLayout(connection_group)
        connection_layout.setVerticalSpacing(15)
        connection_layout.setLabelAlignment(Qt.AlignRight)
        
        # Connection name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Optional connection name")
        self.name_edit.setMinimumHeight(35)
        self.name_edit.setStyleSheet(self._get_input_style())
        connection_layout.addRow(self._create_label("Name:"), self.name_edit)
        
        # Host
        self.host_edit = QLineEdit("localhost")
        self.host_edit.setPlaceholderText("MongoDB server address")
        self.host_edit.setMinimumHeight(35)
        self.host_edit.setStyleSheet(self._get_input_style())
        connection_layout.addRow(self._create_label("Host:"), self.host_edit)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(27017)
        self.port_spin.setMinimumHeight(35)
        self.port_spin.setStyleSheet(self._get_input_style())
        connection_layout.addRow(self._create_label("Port:"), self.port_spin)
        
        layout.addWidget(connection_group)
        
        # Authentication settings
        auth_group = QGroupBox("Authentication")
        auth_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: white;
                border-radius: 5px;
                background: qlineargradient(y1:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        auth_layout = QFormLayout(auth_group)
        auth_layout.setVerticalSpacing(15)
        auth_layout.setLabelAlignment(Qt.AlignRight)
        
        # Enable authentication
        self.auth_enabled_cb = QCheckBox("Enable Authentication")
        self.auth_enabled_cb.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #1976d2;
            }
            QCheckBox::indicator:checked {
                background-color: #1976d2;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik05IDFMMy41IDdMMSA0LjUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
        self.auth_enabled_cb.toggled.connect(self.toggle_auth_fields)
        auth_layout.addRow(self.auth_enabled_cb)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        self.username_edit.setMinimumHeight(35)
        self.username_edit.setStyleSheet(self._get_input_style())
        auth_layout.addRow(self._create_label("Username:"), self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setEnabled(False)
        self.password_edit.setMinimumHeight(35)
        self.password_edit.setStyleSheet(self._get_input_style())
        auth_layout.addRow(self._create_label("Password:"), self.password_edit)

        # Authentication database
        self.auth_db_edit = QLineEdit("admin")
        self.auth_db_edit.setEnabled(False)
        self.auth_db_edit.setMinimumHeight(35)
        self.auth_db_edit.setStyleSheet(self._get_input_style())
        auth_layout.addRow(self._create_label("Auth Database:"), self.auth_db_edit)
        
        layout.addWidget(auth_group)
        
        layout.addStretch()
    
    def _create_label(self, text):
        """Create a styled label for form fields."""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                min-width: 120px;
            }
        """)
        return label
    
    def _get_input_style(self):
        """Get the common input field style."""
        return """
            QLineEdit, QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                selection-background-color: #1976d2;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #1976d2;
                outline: none;
            }
            QLineEdit:disabled, QSpinBox:disabled {
                background-color: #f5f5f5;
                color: #999;
                border-color: #ccc;
            }
        """
    
    def toggle_auth_fields(self, enabled: bool):
        """Enable/disable authentication fields."""
        self.username_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        self.auth_db_edit.setEnabled(enabled)
        
        if not enabled:
            self.username_edit.clear()
            self.password_edit.clear()
    
    def get_connection_info(self) -> ConnectionInfo:
        """Get connection information from the form."""
        return ConnectionInfo(
            name=self.name_edit.text().strip(),
            host=self.host_edit.text().strip() or "localhost",
            port=self.port_spin.value(),
            auth_enabled=self.auth_enabled_cb.isChecked(),
            username=self.username_edit.text().strip() if self.auth_enabled_cb.isChecked() else None,
            password=self.password_edit.text() if self.auth_enabled_cb.isChecked() else None,
            auth_database=self.auth_db_edit.text().strip() if self.auth_enabled_cb.isChecked() else "admin"
        )
    
    def set_connection_info(self, connection: ConnectionInfo):
        """Set connection information in the form."""
        self.name_edit.setText(connection.name or "")
        self.host_edit.setText(connection.host)
        self.port_spin.setValue(connection.port)
        self.auth_enabled_cb.setChecked(connection.auth_enabled)
        
        if connection.auth_enabled:
            self.username_edit.setText(connection.username or "")
            self.password_edit.setText(connection.password or "")
            self.auth_db_edit.setText(connection.auth_database)


class AdvancedConnectionWidget(QWidget):
    """Widget for advanced connection settings."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the advanced connection UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Timeout settings
        timeout_group = QGroupBox("Timeout Settings")
        timeout_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: white;
                border-radius: 5px;
                background: qlineargradient(y1:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        timeout_layout = QFormLayout(timeout_group)
        timeout_layout.setVerticalSpacing(15)
        timeout_layout.setLabelAlignment(Qt.AlignRight)
        
        self.connection_timeout_spin = QSpinBox()
        self.connection_timeout_spin.setRange(1000, 60000)
        self.connection_timeout_spin.setValue(5000)
        self.connection_timeout_spin.setSuffix(" ms")
        self.connection_timeout_spin.setMinimumHeight(35)
        self.connection_timeout_spin.setStyleSheet(self._get_input_style())
        timeout_layout.addRow(self._create_label("Connection Timeout:"), self.connection_timeout_spin)
        
        self.server_selection_timeout_spin = QSpinBox()
        self.server_selection_timeout_spin.setRange(1000, 60000)
        self.server_selection_timeout_spin.setValue(5000)
        self.server_selection_timeout_spin.setSuffix(" ms")
        self.server_selection_timeout_spin.setMinimumHeight(35)
        self.server_selection_timeout_spin.setStyleSheet(self._get_input_style())
        timeout_layout.addRow(self._create_label("Server Selection Timeout:"), self.server_selection_timeout_spin)
        
        layout.addWidget(timeout_group)
        
        # SSL settings
        ssl_group = QGroupBox("SSL/TLS Settings")
        ssl_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: white;
                border-radius: 5px;
                background: qlineargradient(y1:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        ssl_layout = QFormLayout(ssl_group)
        ssl_layout.setVerticalSpacing(15)
        ssl_layout.setLabelAlignment(Qt.AlignRight)
        
        self.ssl_enabled_cb = QCheckBox("Enable SSL/TLS")
        self.ssl_enabled_cb.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #1976d2;
            }
            QCheckBox::indicator:checked {
                background-color: #1976d2;
            }
        """)
        self.ssl_enabled_cb.toggled.connect(self.toggle_ssl_fields)
        ssl_layout.addRow(self.ssl_enabled_cb)
        
        self.ssl_cert_edit = QLineEdit()
        self.ssl_cert_edit.setEnabled(False)
        self.ssl_cert_edit.setPlaceholderText("Path to SSL certificate file")
        self.ssl_cert_edit.setMinimumHeight(35)
        self.ssl_cert_edit.setStyleSheet(self._get_input_style())
        ssl_layout.addRow(self._create_label("Certificate File:"), self.ssl_cert_edit)
        
        layout.addWidget(ssl_group)
        
        # Connection pool settings
        pool_group = QGroupBox("Connection Pool")
        pool_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #1976d2;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 10px;
                background-color: white;
                border-radius: 5px;
                background: qlineargradient(y1:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
            }
        """)
        pool_layout = QFormLayout(pool_group)
        pool_layout.setVerticalSpacing(15)
        pool_layout.setLabelAlignment(Qt.AlignRight)
        
        self.max_pool_size_spin = QSpinBox()
        self.max_pool_size_spin.setRange(1, 100)
        self.max_pool_size_spin.setValue(50)
        self.max_pool_size_spin.setMinimumHeight(35)
        self.max_pool_size_spin.setStyleSheet(self._get_input_style())
        pool_layout.addRow(self._create_label("Max Pool Size:"), self.max_pool_size_spin)
        
        layout.addWidget(pool_group)
        
        layout.addStretch()
    
    def _create_label(self, text):
        """Create a styled label for form fields."""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                min-width: 150px;
            }
        """)
        return label
    
    def _get_input_style(self):
        """Get the common input field style."""
        return """
            QLineEdit, QSpinBox {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                selection-background-color: #1976d2;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #1976d2;
                outline: none;
            }
            QLineEdit:disabled, QSpinBox:disabled {
                background-color: #f5f5f5;
                color: #999;
                border-color: #ccc;
            }
        """
    
    def toggle_ssl_fields(self, enabled: bool):
        """Enable/disable SSL fields."""
        self.ssl_cert_edit.setEnabled(enabled)
    
    def apply_to_connection(self, connection: ConnectionInfo):
        """Apply advanced settings to connection info."""
        connection.connection_timeout = self.connection_timeout_spin.value()
        connection.server_selection_timeout = self.server_selection_timeout_spin.value()
        connection.ssl_enabled = self.ssl_enabled_cb.isChecked()
        connection.ssl_cert_path = self.ssl_cert_edit.text().strip() if self.ssl_enabled_cb.isChecked() else None
        connection.max_pool_size = self.max_pool_size_spin.value()


class ConnectionDialog(QDialog):
    """
    Enhanced connection dialog for MongoDB databases.
    
    Provides comprehensive connection options including recent connections,
    basic and advanced settings, and connection testing.
    """
    
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.logger = get_logger(__name__)
        self.test_worker = None
        self.dragging = False
        self.drag_position = None
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Connect to MongoDB")
        # Set frameless window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #fafafa; border-radius: 12px;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(25, 20, 25, 25)
        content_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("MongoDB Connection")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(20)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: black;
                padding: 15px 0px;
                background: transparent;
                border: none;
                margin: 0px;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        content_layout.addWidget(title_label)
        
        # Main content horizontal layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Recent connections (left side)
        if self.controller:
            self.recent_widget = RecentConnectionsWidget(self.controller)
            self.recent_widget.setMinimumWidth(350)
            self.recent_widget.setMaximumWidth(400)
            self.recent_widget.setStyleSheet("""
                RecentConnectionsWidget {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                }
            """)
            main_layout.addWidget(self.recent_widget)
        
        # Connection settings (right side)
        settings_widget = QWidget()
        settings_widget.setMinimumWidth(450)
        settings_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 10px;
                border: none;
            }
        """)
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 10, 0, 0)
        
        # Tab widget for connection settings with cleaner styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e0e0e0;
                background-color: white;
                margin-top: 0px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: transparent;
                color: #666;
                padding: 14px 28px;
                margin-right: 4px;
                border: 2px solid #e0e0e0;
                font-size: 14px;
                font-weight: 500;
                min-width: 100px;
                border-bottom: 3px solid #e0e0e0;
            }
            QTabBar::tab:selected {
                color: #1976d2;
                font-weight: 600;
                border-bottom: 3px solid #1976d2;
            }
            QTabBar::tab:hover:!selected {
                color: #1976d2;
            }
        """)
        
        # Basic settings tab
        self.basic_widget = BasicConnectionWidget()
        self.tab_widget.addTab(self.basic_widget, "Basic")
        
        # Advanced settings tab
        self.advanced_widget = AdvancedConnectionWidget()
        self.tab_widget.addTab(self.advanced_widget, "Advanced")
        
        settings_layout.addWidget(self.tab_widget)
        main_layout.addWidget(settings_widget)
        
        # Add the horizontal layout to the content layout
        content_layout.addLayout(main_layout)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                font-weight: 500;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976d2, stop:1 #42a5f5);
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(25)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 5px 10px;
                border-radius: 5px;
                background-color: transparent;
            }
        """)
        content_layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setIcon(qta.icon('fa5s.vial', color='white'))
        self.test_btn.setObjectName("test_button")
        self.test_btn.setMinimumHeight(45)
        self.test_btn.setMinimumWidth(140)
        self.test_btn.setToolTip("Test the database connection")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(255, 152, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #f57c00;
                box-shadow: 0 3px 6px rgba(255, 152, 0, 0.4);
            }
            QPushButton:pressed {
                background-color: #ef6c00;
                box-shadow: 0 1px 2px rgba(255, 152, 0, 0.2);
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
                box-shadow: none;
            }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setIcon(qta.icon('fa5s.times', color='#666'))
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.setMinimumWidth(110)
        self.cancel_btn.setToolTip("Cancel connection")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: 2px solid #e0e0e0;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border-color: #ccc;
                color: #333;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
                border-color: #999;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setIcon(qta.icon('fa5s.plug', color='white'))
        self.connect_btn.setObjectName("connect_button")
        self.connect_btn.setDefault(True)
        self.connect_btn.setMinimumHeight(45)
        self.connect_btn.setMinimumWidth(130)
        self.connect_btn.setToolTip("Connect to the database")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #2e7d32);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
                box-shadow: 0 3px 6px rgba(76, 175, 80, 0.3);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #388e3c);
                box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e7d32, stop:1 #1b5e20);
                box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2);
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
                box-shadow: none;
            }
        """)
        self.connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.connect_btn)
        
        content_layout.addLayout(button_layout)
        layout.addWidget(content_widget)
    
    def setup_connections(self):
        """Setup signal connections."""
        if hasattr(self, 'recent_widget'):
            self.recent_widget.connection_selected.connect(self.load_connection)
    
    @pyqtSlot(ConnectionInfo)
    def load_connection(self, connection: ConnectionInfo):
        """Load a connection and automatically connect."""
        self.basic_widget.set_connection_info(connection)
        
        # Switch to basic tab
        self.tab_widget.setCurrentIndex(0)
        
        self.status_label.setText(f"Connecting to: {connection.get_display_name()}")
        
        # Automatically connect (same as clicking the Connect button)
        if self.validate_form():
            super().accept()
    
    def test_connection(self):
        """Test the current connection settings."""
        if not self.controller:
            show_error_message(self, "Error", "No controller available for testing")
            return
        
        # Validate form
        if not self.validate_form():
            return
        
        # Get connection info
        connection_info = self.get_connection_info()
        
        # Show progress
        self.show_progress("Testing connection...")
        
        # Start test worker
        self.test_worker = ConnectionTestWorker(self.controller, connection_info)
        self.test_worker.test_completed.connect(self.on_test_completed)
        self.test_worker.start()
    
    @pyqtSlot(bool, str)
    def on_test_completed(self, success: bool, message: str):
        """Handle connection test completion."""
        self.hide_progress()
        
        if success:
            self.status_label.setText(f"✓ {message}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            show_info_message(self, "Connection Test", message)
        else:
            self.status_label.setText(f"✗ {message}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            show_error_message(self, "Connection Test Failed", message)
        
        # Clean up timer to clear status
        QTimer.singleShot(5000, self.clear_status)
    
    def show_progress(self, message: str):
        """Show progress bar and disable buttons."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText(message)
        self.test_btn.setEnabled(False)
        self.connect_btn.setEnabled(False)
    
    def hide_progress(self):
        """Hide progress bar and enable buttons."""
        self.progress_bar.setVisible(False)
        self.test_btn.setEnabled(True)
        self.connect_btn.setEnabled(True)
    
    def clear_status(self):
        """Clear the status label."""
        self.status_label.setText("")
        self.status_label.setStyleSheet("")
    
    def validate_form(self) -> bool:
        """Validate the connection form."""
        connection_info = self.basic_widget.get_connection_info()
        
        # Basic validation
        if not connection_info.host:
            show_error_message(self, "Validation Error", "Host cannot be empty!")
            self.basic_widget.host_edit.setFocus()
            return False
        
        if connection_info.auth_enabled:
            if not connection_info.username:
                show_error_message(self, "Validation Error", "Username required when authentication is enabled!")
                self.basic_widget.username_edit.setFocus()
                return False
            
            if not connection_info.password:
                show_error_message(self, "Validation Error", "Password required when authentication is enabled!")
                self.basic_widget.password_edit.setFocus()
                return False
        
        return True
        
    # Window dragging functionality
    def mousePressEvent(self, event):
        """Handle mouse press for dragging the window."""
        if hasattr(self, 'title_bar') and self.title_bar.underMouse() and event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging the window."""
        if hasattr(self, 'dragging') and self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for dragging the window."""
        if hasattr(self, 'dragging'):
            self.dragging = False
    
    def get_connection_info(self) -> ConnectionInfo:
        """Get the complete connection information."""
        connection_info = self.basic_widget.get_connection_info()
        self.advanced_widget.apply_to_connection(connection_info)
        return connection_info
    
    def accept(self):
        """Accept the dialog after validation."""
        if self.validate_form():
            super().accept()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop any running test worker
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.terminate()
            self.test_worker.wait()
        
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.connect_btn.isEnabled():
                self.accept()
        else:
            super().keyPressEvent(event)
