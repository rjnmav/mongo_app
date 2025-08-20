"""
Main window for the MongoDB Visualizer application.

This module provides the main application window with a professional,
modern interface following Qt design patterns and best practices.
"""

import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QMenuBar, QStatusBar, QToolBar, QAction, QActionGroup,
    QLabel, QPushButton, QComboBox, QSpinBox, QLineEdit, QGroupBox,
    QFormLayout, QProgressBar, QFrame, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QThread, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeySequence
import qtawesome as qta

from ..controllers.database_controller import DatabaseController
from ..models.data_models import (
    ConnectionInfo, DatabaseInfo, CollectionInfo, ConnectionStatus,
    DocumentStats, QueryInfo, ErrorInfo, ApplicationState
)
from ..utils.helpers import (
    format_bytes, format_number, format_duration, FontHelper,
    SettingsManager, show_error_message, show_info_message, JsonFormatter
)
from ..utils.logging_config import get_logger
from ..styles.theme_manager import theme_manager, ThemeType
from .connection_dialog import ConnectionDialog
from .document_viewer import DocumentViewer
from .syntax_highlighter import JsonSyntaxHighlighter


class StatusBarWidget(QWidget):
    """Custom status bar widget with multiple status indicators."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Connection status
        self.connection_label = QLabel("Disconnected")
        self.connection_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        layout.addWidget(self.connection_label)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator1)
        
        # Current selection
        self.selection_label = QLabel("No selection")
        layout.addWidget(self.selection_label)
        
        # Spacer
        layout.addStretch()
        
        # Performance info
        self.performance_label = QLabel("")
        layout.addWidget(self.performance_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)
    
    def update_connection_status(self, status: ConnectionStatus, connection: ConnectionInfo = None):
        """Update connection status display."""
        if status == ConnectionStatus.CONNECTED:
            self.connection_label.setText(f"Connected to {connection.get_display_name()}")
            self.connection_label.setStyleSheet("color: #388e3c; font-weight: bold;")
        elif status == ConnectionStatus.CONNECTING:
            self.connection_label.setText("Connecting...")
            self.connection_label.setStyleSheet("color: #f57c00; font-weight: bold;")
        elif status == ConnectionStatus.ERROR:
            self.connection_label.setText("Connection Error")
            self.connection_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        else:
            self.connection_label.setText("Disconnected")
            self.connection_label.setStyleSheet("color: #757575; font-weight: bold;")
    
    def update_selection(self, database: str = None, collection: str = None):
        """Update current selection display."""
        if database and collection:
            self.selection_label.setText(f"Database: {database} | Collection: {collection}")
        elif database:
            self.selection_label.setText(f"Database: {database}")
        else:
            self.selection_label.setText("No selection")
    
    def update_performance(self, operation: str, duration: float, count: int = None):
        """Update performance information."""
        text = f"Last operation: {operation} ({format_duration(duration)})"
        if count is not None:
            text += f" | {format_number(count)} items"
        self.performance_label.setText(text)
    
    def show_progress(self, message: str = "Working..."):
        """Show progress bar with message."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.connection_label.setText(message)
    
    def hide_progress(self):
        """Hide progress bar."""
        self.progress_bar.setVisible(False)


class DatabaseTreeWidget(QTreeWidget):
    """Custom tree widget for database structure display."""
    
    def __init__(self, controller: DatabaseController):
        super().__init__()
        self.controller = controller
        self.logger = get_logger(__name__)
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the tree widget UI."""
        self.setHeaderLabel("Database Structure")
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Tree widget styling is now handled by the global theme
    
    def setup_connections(self):
        """Setup signal connections."""
        self.itemClicked.connect(self.on_item_clicked)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.itemExpanded.connect(self.on_item_expanded)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def populate_databases(self, databases: List[DatabaseInfo]):
        """Populate the tree with database information."""
        self.clear()
        
        for db_info in databases:
            db_item = QTreeWidgetItem(self)
            db_item.setText(0, db_info.name)
            db_item.setIcon(0, qta.icon('fa5s.database', color='#2c3e50'))
            db_item.setData(0, Qt.UserRole, {'type': 'database', 'info': db_info})
            
            # Add database info as tooltip
            tooltip = f"Database: {db_info.name}\n"
            tooltip += f"Collections: {db_info.collection_count}\n"
            tooltip += f"Data Size: {db_info.get_formatted_data_size()}\n"
            tooltip += f"Storage Size: {format_bytes(db_info.storage_size)}"
            db_item.setToolTip(0, tooltip)
            
            # Add loading placeholder for collections
            loading_item = QTreeWidgetItem(db_item)
            loading_item.setText(0, "Loading...")
            loading_item.setData(0, Qt.UserRole, {'type': 'loading'})
    
    def populate_collections(self, database_name: str, collections: List[CollectionInfo]):
        """Populate collections for a specific database."""
        # Find the database item
        db_item = None
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            item_data = item.data(0, Qt.UserRole)
            if item_data and item_data['type'] == 'database' and item_data['info'].name == database_name:
                db_item = item
                break
        
        if not db_item:
            return
        
        # Clear existing children
        db_item.takeChildren()
        
        # Add collections
        for coll_info in collections:
            coll_item = QTreeWidgetItem(db_item)
            coll_item.setText(0, coll_info.name)
            coll_item.setIcon(0, qta.icon('fa5s.table', color='#3498db'))
            coll_item.setData(0, Qt.UserRole, {'type': 'collection', 'info': coll_info})
            
            # Add collection info as tooltip
            tooltip = f"Collection: {coll_info.name}\n"
            tooltip += f"Documents: {format_number(coll_info.document_count)}\n"
            tooltip += f"Data Size: {coll_info.get_formatted_data_size()}\n"
            tooltip += f"Indexes: {coll_info.index_count}\n"
            tooltip += f"Average Doc Size: {format_bytes(int(coll_info.avg_document_size))}"
            coll_item.setToolTip(0, tooltip)
        
        # Expand the database item
        db_item.setExpanded(True)
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click events."""
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        if item_data['type'] == 'database':
            db_info = item_data['info']
            self.logger.debug(f"Selected database: {db_info.name}")
            
            # Load collections if not already loaded
            if item.childCount() == 1 and item.child(0).data(0, Qt.UserRole)['type'] == 'loading':
                self.controller.load_collections(db_info.name)
        
        elif item_data['type'] == 'collection':
            coll_info = item_data['info']
            self.logger.debug(f"Selected collection: {coll_info.get_full_name()}")
    
    @pyqtSlot(QTreeWidgetItem, int)
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double-click events."""
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        if item_data['type'] == 'collection':
            coll_info = item_data['info']
            self.logger.info(f"Loading documents from {coll_info.get_full_name()}")
            self.controller.load_documents(coll_info.database, coll_info.name)
    
    @pyqtSlot(QTreeWidgetItem)
    def on_item_expanded(self, item: QTreeWidgetItem):
        """Handle item expansion events (when arrow is clicked)."""
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return
        
        if item_data['type'] == 'database':
            db_info = item_data['info']
            self.logger.debug(f"Expanded database: {db_info.name}")
            
            # Load collections if not already loaded
            if item.childCount() == 1 and item.child(0).data(0, Qt.UserRole)['type'] == 'loading':
                self.controller.load_collections(db_info.name)
    
    def show_context_menu(self, position):
        """Show context menu for tree items."""
        # TODO: Implement context menu with refresh, export, etc.
        pass


class MainWindow(QMainWindow):
    """
    Main application window for MongoDB Visualizer.
    
    Provides a professional interface with database tree, document viewer,
    query execution, and comprehensive status monitoring.
    """
    
    def __init__(self):
        super().__init__()
        # Import config here to avoid circular imports
        from ..config.settings import get_config
        self.config = get_config()
        self.controller = DatabaseController(self.config)
        self.settings_manager = SettingsManager()
        self.logger = get_logger(__name__)
        
        # UI components
        self.database_tree = None
        self.document_viewer = None
        self.status_widget = None
        
        # Initialize UI
        self.init_ui()
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()
        self.setup_connections()
        self.restore_settings()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        
        self.logger.info("Main window initialized")
        
        # Auto-connect to localhost on startup (delayed to ensure UI is ready)
        QTimer.singleShot(500, self.auto_connect_localhost)
    
    def init_ui(self):
        """Initialize the main user interface."""
        self.setWindowTitle("MongoDB Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Create left panel (database tree)
        self.create_left_panel(main_splitter)
        
        # Create right panel (document viewer)
        self.create_right_panel(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([350, 1050])
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        
        # Store splitter for settings
        self.main_splitter = main_splitter
    
    def create_left_panel(self, parent):
        """Create the left panel with database tree."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Database tree
        self.database_tree = DatabaseTreeWidget(self.controller)
        left_layout.addWidget(self.database_tree)
        
        # Quick actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(5, 5, 5, 5)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        refresh_btn.setObjectName("refresh_button")
        refresh_btn.setToolTip("Refresh database structure")
        refresh_btn.clicked.connect(self.refresh_databases)
        actions_layout.addWidget(refresh_btn)
        
        actions_layout.addStretch()
        
        left_layout.addWidget(actions_widget)
        
        parent.addWidget(left_widget)
    
    def create_right_panel(self, parent):
        """Create the right panel with document viewer."""
        self.document_viewer = DocumentViewer(self.controller)
        parent.addWidget(self.document_viewer)
    
    def create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        # Connection actions
        connect_action = QAction('&Connect to Database...', self)
        connect_action.setShortcut(QKeySequence.New)
        connect_action.setStatusTip('Connect to a MongoDB database')
        connect_action.triggered.connect(self.show_connection_dialog)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction('&Disconnect', self)
        disconnect_action.setStatusTip('Disconnect from current database')
        disconnect_action.triggered.connect(self.disconnect_database)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        # Recent connections submenu
        self.recent_menu = file_menu.addMenu('Recent Connections')
        self.update_recent_connections_menu()
        
        file_menu.addSeparator()
        
        # Auto-connect toggle
        self.auto_connect_action = QAction('Auto-Connect to Localhost', self)
        self.auto_connect_action.setCheckable(True)
        self.auto_connect_action.setChecked(self.config.database.auto_connect_localhost)
        self.auto_connect_action.setStatusTip('Automatically connect to localhost MongoDB on startup')
        self.auto_connect_action.toggled.connect(self.toggle_auto_connect)
        file_menu.addAction(self.auto_connect_action)
        
        file_menu.addSeparator()
        
        # Export actions
        export_action = QAction('&Export Data...', self)
        export_action.setShortcut(QKeySequence.SaveAs)
        export_action.setStatusTip('Export current data to file')
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        refresh_action = QAction('&Refresh', self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.setStatusTip('Refresh current view')
        refresh_action.triggered.connect(self.refresh_current_view)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Auto-refresh toggle
        self.auto_refresh_action = QAction('Auto Refresh', self)
        self.auto_refresh_action.setCheckable(True)
        self.auto_refresh_action.setStatusTip('Enable automatic refresh every 30 seconds')
        self.auto_refresh_action.toggled.connect(self.toggle_auto_refresh)
        view_menu.addAction(self.auto_refresh_action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu('&Themes')
        theme_menu.setStatusTip('Change application theme')
        
        theme_action_group = QActionGroup(self)
        
        # Light theme
        light_theme_action = QAction('&Light Theme', self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(theme_manager.get_current_theme() == ThemeType.LIGHT)
        light_theme_action.triggered.connect(lambda: self.change_theme(ThemeType.LIGHT))
        theme_action_group.addAction(light_theme_action)
        theme_menu.addAction(light_theme_action)
        
        # Dark theme
        dark_theme_action = QAction('&Dark Theme', self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(theme_manager.get_current_theme() == ThemeType.DARK)
        dark_theme_action.triggered.connect(lambda: self.change_theme(ThemeType.DARK))
        theme_action_group.addAction(dark_theme_action)
        theme_menu.addAction(dark_theme_action)
        
        # Blue theme
        blue_theme_action = QAction('&Blue Theme', self)
        blue_theme_action.setCheckable(True)
        blue_theme_action.setChecked(theme_manager.get_current_theme() == ThemeType.BLUE)
        blue_theme_action.triggered.connect(lambda: self.change_theme(ThemeType.BLUE))
        theme_action_group.addAction(blue_theme_action)
        theme_menu.addAction(blue_theme_action)
        
        # Green theme
        green_theme_action = QAction('&Green Theme', self)
        green_theme_action.setCheckable(True)
        green_theme_action.setChecked(theme_manager.get_current_theme() == ThemeType.GREEN)
        green_theme_action.triggered.connect(lambda: self.change_theme(ThemeType.GREEN))
        theme_action_group.addAction(green_theme_action)
        theme_menu.addAction(green_theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        query_action = QAction('&Query Builder...', self)
        query_action.setShortcut('Ctrl+Q')
        query_action.setStatusTip('Open query builder')
        query_action.triggered.connect(self.show_query_builder)
        tools_menu.addAction(query_action)
        
        performance_action = QAction('&Performance Monitor...', self)
        performance_action.setStatusTip('View performance metrics')
        performance_action.triggered.connect(self.show_performance_monitor)
        tools_menu.addAction(performance_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About...', self)
        about_action.setStatusTip('About MongoDB Visualizer')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbars(self):
        """Create application toolbars."""
        # Main toolbar
        main_toolbar = self.addToolBar('Main')
        main_toolbar.setObjectName('MainToolBar')
        main_toolbar.setMovable(False)
        main_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        main_toolbar.setIconSize(QSize(20, 20))
        
        # Connection buttons
        connect_action = QAction(qta.icon('fa5s.plug', color='white'), 'Connect', self)
        connect_action.setStatusTip('Connect to a MongoDB database')
        connect_action.triggered.connect(self.show_connection_dialog)
        main_toolbar.addAction(connect_action)
        
        disconnect_action = QAction(qta.icon('fa5s.times-circle', color='white'), 'Disconnect', self)
        disconnect_action.setStatusTip('Disconnect from current database')
        disconnect_action.triggered.connect(self.disconnect_database)
        main_toolbar.addAction(disconnect_action)
        
        main_toolbar.addSeparator()
        
        # View buttons
        refresh_action = QAction(qta.icon('fa5s.sync-alt', color='white'), 'Refresh', self)
        refresh_action.setStatusTip('Refresh current view')
        refresh_action.triggered.connect(self.refresh_current_view)
        main_toolbar.addAction(refresh_action)
        
        export_action = QAction(qta.icon('fa5s.download', color='white'), 'Export', self)
        export_action.setStatusTip('Export current data to file')
        export_action.triggered.connect(self.export_data)
        main_toolbar.addAction(export_action)
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_widget = StatusBarWidget()
        self.statusBar().addWidget(self.status_widget, 1)
    
    def setup_connections(self):
        """Setup signal connections with the controller."""
        self.controller.connection_status_changed.connect(self.on_connection_status_changed)
        self.controller.databases_loaded.connect(self.on_databases_loaded)
        self.controller.collections_loaded.connect(self.on_collections_loaded)
        self.controller.documents_loaded.connect(self.on_documents_loaded)
        self.controller.query_executed.connect(self.on_query_executed)
        self.controller.error_occurred.connect(self.on_error_occurred)
        self.controller.performance_updated.connect(self.on_performance_updated)
    
    def restore_settings(self):
        """Restore application settings."""
        self.settings_manager.restore_window_geometry(self)
        self.settings_manager.restore_splitter_state(self.main_splitter, "main")
        
        # Restore auto-refresh setting
        auto_refresh = self.settings_manager.get_value("auto_refresh", False)
        self.auto_refresh_action.setChecked(auto_refresh)
        if auto_refresh:
            self.toggle_auto_refresh(True)
    
    def save_settings(self):
        """Save application settings."""
        self.settings_manager.save_window_geometry(self)
        self.settings_manager.save_splitter_state(self.main_splitter, "main")
        self.settings_manager.save_value("auto_refresh", self.auto_refresh_action.isChecked())
        self.settings_manager.sync()
    
    # Slot methods for controller signals
    
    @pyqtSlot(ConnectionStatus)
    def on_connection_status_changed(self, status: ConnectionStatus):
        """Handle connection status changes."""
        state = self.controller.get_application_state()
        self.status_widget.update_connection_status(status, state.current_connection)
        
        if status == ConnectionStatus.CONNECTED:
            self.logger.info("Connected to database successfully")
        elif status == ConnectionStatus.ERROR:
            self.logger.warning("Database connection error")
    
    @pyqtSlot(list)
    def on_databases_loaded(self, databases: List[DatabaseInfo]):
        """Handle databases loaded event."""
        self.database_tree.populate_databases(databases)
        self.status_widget.update_performance("Load databases", 0.1, len(databases))
        self.logger.info(f"Loaded {len(databases)} databases")
    
    @pyqtSlot(str, list)
    def on_collections_loaded(self, database_name: str, collections: List[CollectionInfo]):
        """Handle collections loaded event."""
        self.database_tree.populate_collections(database_name, collections)
        self.status_widget.update_selection(database_name)
        self.logger.info(f"Loaded {len(collections)} collections for database {database_name}")
    
    @pyqtSlot(str, str, list, DocumentStats)
    def on_documents_loaded(self, database: str, collection: str, documents: list, stats: DocumentStats):
        """Handle documents loaded event."""
        self.document_viewer.display_documents(documents, database, collection, stats)
        self.status_widget.update_selection(database, collection)
        self.status_widget.update_performance("Load documents", 0.5, len(documents))
        self.logger.info(f"Loaded {len(documents)} documents from {database}.{collection}")
    
    @pyqtSlot(QueryInfo)
    def on_query_executed(self, query_info: QueryInfo):
        """Handle query execution completion."""
        if query_info.error:
            show_error_message(self, "Query Error", query_info.error)
        else:
            duration = query_info.execution_time or 0
            count = query_info.result_count
            self.status_widget.update_performance("Execute query", duration, count)
            self.logger.info(f"Query executed successfully in {format_duration(duration)}")
    
    @pyqtSlot(ErrorInfo)
    def on_error_occurred(self, error_info: ErrorInfo):
        """Handle error events."""
        show_error_message(
            self,
            "Error",
            error_info.message,
            error_info.stack_trace
        )
        self.logger.error(f"Error: {error_info.message}")
    
    @pyqtSlot(object)
    def on_performance_updated(self, metrics):
        """Handle performance metric updates."""
        # Update performance display if needed
        pass
    
    # Action methods
    
    def show_connection_dialog(self):
        """Show the database connection dialog."""
        dialog = ConnectionDialog(self, self.controller)
        if dialog.exec_() == dialog.Accepted:
            connection_info = dialog.get_connection_info()
            self.controller.connect_to_database(connection_info)
            self.update_recent_connections_menu()
    
    def auto_connect_localhost(self):
        """Automatically connect to localhost MongoDB on startup."""
        # Check if auto-connect is enabled in configuration
        if not self.config.database.auto_connect_localhost:
            self.logger.info("Auto-connection to localhost is disabled in configuration")
            return
            
        try:
            # Create default localhost connection info using config values
            localhost_connection = ConnectionInfo(
                name="Localhost (Auto)",
                host=self.config.database.default_host,
                port=self.config.database.default_port,
                auth_enabled=False
            )
            
            # Attempt auto-connection
            self.logger.info(f"Attempting auto-connection to {localhost_connection.host}:{localhost_connection.port}...")
            self.controller.connect_to_database(localhost_connection)
            
        except Exception as e:
            self.logger.warning(f"Auto-connection to localhost failed: {e}")
            # Silently fail - user can manually connect if needed
    
    def disconnect_database(self):
        """Disconnect from the current database."""
        self.controller.disconnect_from_database()
        self.database_tree.clear()
        self.document_viewer.clear()
        self.status_widget.update_selection()
    
    def refresh_databases(self):
        """Refresh the database list."""
        self.controller.load_databases()
    
    def refresh_current_view(self):
        """Refresh the current view."""
        state = self.controller.get_application_state()
        if state.has_selection():
            self.controller.load_documents(
                state.current_database,
                state.current_collection,
                state.query_limit,
                state.query_skip
            )
        else:
            self.refresh_databases()
    
    def toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality."""
        if enabled:
            self.refresh_timer.start(30000)  # 30 seconds
            self.logger.info("Auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.logger.info("Auto-refresh disabled")
    
    def toggle_auto_connect(self, enabled: bool):
        """Toggle auto-connect to localhost functionality."""
        self.config.database.auto_connect_localhost = enabled
        self.config.save_config()
        if enabled:
            self.logger.info("Auto-connect to localhost enabled")
        else:
            self.logger.info("Auto-connect to localhost disabled")
    
    def auto_refresh(self):
        """Perform auto-refresh."""
        state = self.controller.get_application_state()
        if state.is_connected() and state.has_selection():
            self.refresh_current_view()
    
    def export_data(self):
        """Export current data to file."""
        # TODO: Implement data export dialog
        show_info_message(self, "Export", "Export functionality coming soon!")
    
    def show_query_builder(self):
        """Show the query builder dialog."""
        # TODO: Implement query builder
        show_info_message(self, "Query Builder", "Query builder coming soon!")
    
    def show_performance_monitor(self):
        """Show the performance monitor dialog."""
        # TODO: Implement performance monitor
        show_info_message(self, "Performance Monitor", "Performance monitor coming soon!")
    
    def change_theme(self, theme: ThemeType):
        """Change the application theme."""
        try:
            theme_manager.set_theme(theme)
            self.logger.info(f"Changed theme to: {theme.value}")
            show_info_message(self, "Theme Changed", f"Successfully changed to {theme.value.title()} theme!")
        except Exception as e:
            self.logger.error(f"Failed to change theme: {e}")
            show_error_message(self, "Theme Error", f"Failed to change theme: {str(e)}")
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
        <h2>MongoDB Visualizer</h2>
        <p>Version 1.0.0</p>
        <p>A professional PyQt5-based desktop application for MongoDB database visualization and management.</p>
        <p>Features:</p>
        <ul>
        <li>Database and collection browsing</li>
        <li>Document visualization and analysis</li>
        <li>Query execution and history</li>
        <li>Performance monitoring</li>
        <li>Data export capabilities</li>
        </ul>
        <p>Built with PyQt5 and PyMongo</p>
        """
        
        from PyQt5.QtWidgets import QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About MongoDB Visualizer")
        msg_box.setText(about_text)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.exec_()
    
    def update_recent_connections_menu(self):
        """Update the recent connections menu."""
        self.recent_menu.clear()
        
        recent_connections = self.controller.get_recent_connections()
        for connection in recent_connections:
            action = self.recent_menu.addAction(connection.get_display_name())
            action.triggered.connect(
                lambda checked, conn=connection: self.controller.connect_to_database(conn)
            )
        
        if not recent_connections:
            action = self.recent_menu.addAction("No recent connections")
            action.setEnabled(False)
    
    # Event overrides
    
    def closeEvent(self, event):
        """Handle application close event."""
        self.save_settings()
        self.controller.disconnect_from_database()
        event.accept()
        self.logger.info("Application closed")
