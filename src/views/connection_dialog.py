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
    QSplitter, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QIcon

from ..models.data_models import ConnectionInfo, ConnectionStatus
from ..utils.helpers import show_error_message, show_info_message
from ..utils.logging_config import get_logger


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
        
        # Header
        header_label = QLabel("Recent Connections")
        header_font = QFont()
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Instruction label
        instruction_label = QLabel("Click on a connection to connect immediately")
        instruction_label.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        layout.addWidget(instruction_label)
        
        # Connections list
        self.connections_list = QListWidget()
        self.connections_list.itemDoubleClicked.connect(self.on_connection_double_clicked)
        self.connections_list.itemClicked.connect(self.on_connection_clicked)
        layout.addWidget(self.connections_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_selected)
        button_layout.addWidget(connect_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_recent_connections)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
    
    def load_recent_connections(self):
        """Load recent connections from the controller."""
        self.connections_list.clear()
        
        recent_connections = self.controller.get_recent_connections()
        for connection in recent_connections:
            item = QListWidgetItem(connection.get_display_name())
            item.setData(Qt.UserRole, connection)
            
            # Add tooltip with connection details
            tooltip = f"Host: {connection.host}:{connection.port}\n"
            if connection.auth_enabled:
                tooltip += f"Username: {connection.username}\n"
                tooltip += f"Auth DB: {connection.auth_database}"
            else:
                tooltip += "No authentication"
            item.setToolTip(tooltip)
            
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
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout(connection_group)
        
        # Connection name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Optional connection name")
        connection_layout.addRow("Name:", self.name_edit)
        
        # Host
        self.host_edit = QLineEdit("localhost")
        self.host_edit.setPlaceholderText("MongoDB server address")
        connection_layout.addRow("Host:", self.host_edit)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(27017)
        connection_layout.addRow("Port:", self.port_spin)
        
        layout.addWidget(connection_group)
        
        # Authentication settings
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout(auth_group)
        
        # Enable authentication
        self.auth_enabled_cb = QCheckBox("Enable Authentication")
        self.auth_enabled_cb.toggled.connect(self.toggle_auth_fields)
        auth_layout.addRow(self.auth_enabled_cb)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(False)
        auth_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setEnabled(False)
        auth_layout.addRow("Password:", self.password_edit)
        
        # Authentication database
        self.auth_db_edit = QLineEdit("admin")
        self.auth_db_edit.setEnabled(False)
        auth_layout.addRow("Auth Database:", self.auth_db_edit)
        
        layout.addWidget(auth_group)
        
        layout.addStretch()
    
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
        
        # Timeout settings
        timeout_group = QGroupBox("Timeout Settings")
        timeout_layout = QFormLayout(timeout_group)
        
        self.connection_timeout_spin = QSpinBox()
        self.connection_timeout_spin.setRange(1000, 60000)
        self.connection_timeout_spin.setValue(5000)
        self.connection_timeout_spin.setSuffix(" ms")
        timeout_layout.addRow("Connection Timeout:", self.connection_timeout_spin)
        
        self.server_selection_timeout_spin = QSpinBox()
        self.server_selection_timeout_spin.setRange(1000, 60000)
        self.server_selection_timeout_spin.setValue(5000)
        self.server_selection_timeout_spin.setSuffix(" ms")
        timeout_layout.addRow("Server Selection Timeout:", self.server_selection_timeout_spin)
        
        layout.addWidget(timeout_group)
        
        # SSL settings
        ssl_group = QGroupBox("SSL/TLS Settings")
        ssl_layout = QFormLayout(ssl_group)
        
        self.ssl_enabled_cb = QCheckBox("Enable SSL/TLS")
        self.ssl_enabled_cb.toggled.connect(self.toggle_ssl_fields)
        ssl_layout.addRow(self.ssl_enabled_cb)
        
        self.ssl_cert_edit = QLineEdit()
        self.ssl_cert_edit.setEnabled(False)
        self.ssl_cert_edit.setPlaceholderText("Path to SSL certificate file")
        ssl_layout.addRow("Certificate File:", self.ssl_cert_edit)
        
        layout.addWidget(ssl_group)
        
        # Connection pool settings
        pool_group = QGroupBox("Connection Pool")
        pool_layout = QFormLayout(pool_group)
        
        self.max_pool_size_spin = QSpinBox()
        self.max_pool_size_spin.setRange(1, 100)
        self.max_pool_size_spin.setValue(50)
        pool_layout.addRow("Max Pool Size:", self.max_pool_size_spin)
        
        layout.addWidget(pool_group)
        
        layout.addStretch()
    
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
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setWindowTitle("Connect to MongoDB")
        self.setModal(True)
        self.resize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("MongoDB Connection")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Recent connections (left side)
        if self.controller:
            self.recent_widget = RecentConnectionsWidget(self.controller)
            splitter.addWidget(self.recent_widget)
        
        # Connection settings (right side)
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Tab widget for connection settings
        self.tab_widget = QTabWidget()
        
        # Basic settings tab
        self.basic_widget = BasicConnectionWidget()
        self.tab_widget.addTab(self.basic_widget, "Basic")
        
        # Advanced settings tab
        self.advanced_widget = AdvancedConnectionWidget()
        self.tab_widget.addTab(self.advanced_widget, "Advanced")
        
        settings_layout.addWidget(self.tab_widget)
        splitter.addWidget(settings_widget)
        
        # Set splitter proportions
        splitter.setSizes([250, 350])
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setDefault(True)
        self.connect_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
    
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
