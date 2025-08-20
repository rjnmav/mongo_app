"""
Enhanced document viewer for the MongoDB Visualizer application.

This module provides a comprehensive document viewer with multiple visualization
modes, query execution, and data analysis capabilities.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QSplitter, QGroupBox,
    QFormLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QProgressBar, QCheckBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QColor
import qtawesome as qta

from ..models.data_models import DocumentStats, QueryInfo, QueryType
from ..utils.helpers import (
    format_bytes, format_number, format_duration, FontHelper,
    JsonFormatter, validate_json, validate_mongodb_query
)
from ..utils.logging_config import get_logger
from .syntax_highlighter import JsonSyntaxHighlighter


class QueryWidget(QWidget):
    """Widget for query input and execution."""
    
    query_requested = pyqtSignal(dict, str)  # query, query_type
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the query widget UI (compact version)."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        # Top row: Query type and options
        top_row = QHBoxLayout()
        
        top_row.addWidget(QLabel("Query:"))
        
        self.query_type_combo = QComboBox()
        self.query_type_combo.addItems(["find", "count", "distinct", "aggregate"])
        self.query_type_combo.currentTextChanged.connect(self.on_query_type_changed)
        self.query_type_combo.setMaximumWidth(100)
        top_row.addWidget(self.query_type_combo)
        
        top_row.addWidget(QLabel("Limit:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 1000)
        self.limit_spin.setValue(100)
        self.limit_spin.setMaximumWidth(80)
        top_row.addWidget(self.limit_spin)
        
        top_row.addWidget(QLabel("Skip:"))
        self.skip_spin = QSpinBox()
        self.skip_spin.setRange(0, 10000)
        self.skip_spin.setValue(0)
        self.skip_spin.setMaximumWidth(80)
        top_row.addWidget(self.skip_spin)
        
        top_row.addStretch()
        
        # Execute button
        self.execute_btn = QPushButton("Execute Query")
        self.execute_btn.setIcon(qta.icon('fa5s.play', color='white'))
        self.execute_btn.clicked.connect(self.execute_query)
        self.execute_btn.setMaximumWidth(120)
        top_row.addWidget(self.execute_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setIcon(qta.icon('fa5s.eraser', color='#666'))
        clear_btn.clicked.connect(self.clear_query)
        clear_btn.setMaximumWidth(60)
        top_row.addWidget(clear_btn)
        
        layout.addLayout(top_row)
        
        # Query text editor (much smaller)
        self.query_editor = QTextEdit()
        self.query_editor.setFont(FontHelper.get_monospace_font(9))
        self.query_editor.setMaximumHeight(50)  # Much smaller
        self.query_editor.setPlaceholderText('Enter MongoDB query (e.g., {"status": "active"})')
        
        # Add syntax highlighting
        self.highlighter = JsonSyntaxHighlighter(self.query_editor.document())
        
        layout.addWidget(self.query_editor)
    
    def on_query_type_changed(self, query_type: str):
        """Handle query type change."""
        if query_type == "find":
            self.query_editor.setPlaceholderText('{"field": "value"}')
        elif query_type == "count":
            self.query_editor.setPlaceholderText('{"field": "value"}')
        elif query_type == "distinct":
            self.query_editor.setPlaceholderText('{"field": "_id", "filter": {}}')
        elif query_type == "aggregate":
            self.query_editor.setPlaceholderText('[{"$match": {"field": "value"}}]')
    
    def execute_query(self):
        """Execute the current query."""
        query_text = self.query_editor.toPlainText().strip()
        query_type = self.query_type_combo.currentText()
        
        if not query_text:
            query = {}
        else:
            is_valid, parsed_query, error = validate_json(query_text)
            if not is_valid:
                self.logger.error(f"Invalid JSON query: {error}")
                return
            query = parsed_query
        
        # Validate MongoDB query
        if query_type in ["find", "count"]:
            is_valid, error = validate_mongodb_query(query)
            if not is_valid:
                self.logger.error(f"Invalid MongoDB query: {error}")
                return
        
        self.query_requested.emit(query, query_type)
    
    def clear_query(self):
        """Clear the query editor."""
        self.query_editor.clear()
        self.limit_spin.setValue(100)
        self.skip_spin.setValue(0)
    
    def get_limit(self) -> int:
        """Get the current limit value."""
        return self.limit_spin.value()
    
    def get_skip(self) -> int:
        """Get the current skip value."""
        return self.skip_spin.value()


class DocumentTableWidget(QTableWidget):
    """Enhanced table widget for document display."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the table widget."""
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Configure headers
        horizontal_header = self.horizontalHeader()
        horizontal_header.setStretchLastSection(True)
        horizontal_header.setSectionResizeMode(QHeaderView.Interactive)
        
        vertical_header = self.verticalHeader()
        vertical_header.setVisible(True)
        vertical_header.setDefaultSectionSize(25)
    
    def populate_documents(self, documents: List[Dict[str, Any]]):
        """Populate the table with documents."""
        if not documents:
            self.setRowCount(0)
            self.setColumnCount(0)
            return
        
        try:
            # Get all unique field names
            all_fields = set()
            for doc in documents:
                all_fields.update(doc.keys())
            
            field_list = sorted(list(all_fields))
            
            # Setup table dimensions
            self.setRowCount(len(documents))
            self.setColumnCount(len(field_list))
            self.setHorizontalHeaderLabels(field_list)
            
            # Populate data
            for row, doc in enumerate(documents):
                for col, field in enumerate(field_list):
                    value = doc.get(field, '')
                    
                    # Convert complex values to JSON string
                    if isinstance(value, (dict, list)):
                        display_value = json.dumps(value, default=str)
                    elif value is None:
                        display_value = 'null'
                    else:
                        display_value = str(value)
                    
                    # Truncate very long values
                    if len(display_value) > 100:
                        display_value = display_value[:97] + "..."
                    
                    item = QTableWidgetItem(display_value)
                    item.setToolTip(str(value))
                    self.setItem(row, col, item)
            
            # Auto-resize columns
            self.resizeColumnsToContents()
            
            # Limit column width
            for col in range(self.columnCount()):
                width = self.columnWidth(col)
                if width > 200:
                    self.setColumnWidth(col, 200)
                    
        except Exception as e:
            self.logger.error(f"Error populating table: {e}")


class DocumentTreeWidget(QTreeWidget):
    """Tree widget for hierarchical document display."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the tree widget."""
        self.setHeaderLabels(["Field", "Value", "Type"])
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        
        # Configure headers
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def populate_documents(self, documents: List[Dict[str, Any]]):
        """Populate the tree with documents."""
        self.clear()
        
        if not documents:
            return
        
        for i, doc in enumerate(documents):
            doc_item = QTreeWidgetItem(self)
            doc_item.setText(0, f"Document {i + 1}")
            doc_item.setText(1, f"{len(doc)} fields")
            doc_item.setText(2, "object")
            
            self.populate_object(doc_item, doc)
        
        self.expandToDepth(1)
    
    def populate_object(self, parent_item: QTreeWidgetItem, obj: Any, key: str = None):
        """Recursively populate object in tree."""
        if isinstance(obj, dict):
            for field_key, field_value in obj.items():
                field_item = QTreeWidgetItem(parent_item)
                field_item.setText(0, str(field_key))
                field_item.setText(2, type(field_value).__name__)
                
                if isinstance(field_value, (dict, list)):
                    if isinstance(field_value, dict):
                        field_item.setText(1, f"{len(field_value)} fields")
                    else:
                        field_item.setText(1, f"{len(field_value)} items")
                    self.populate_object(field_item, field_value, field_key)
                else:
                    field_item.setText(1, str(field_value))
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                item_node = QTreeWidgetItem(parent_item)
                item_node.setText(0, f"[{i}]")
                item_node.setText(2, type(item).__name__)
                
                if isinstance(item, (dict, list)):
                    if isinstance(item, dict):
                        item_node.setText(1, f"{len(item)} fields")
                    else:
                        item_node.setText(1, f"{len(item)} items")
                    self.populate_object(item_node, item)
                else:
                    item_node.setText(1, str(item))


class StatisticsWidget(QWidget):
    """Widget for displaying document statistics."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the statistics widget."""
        layout = QVBoxLayout(self)
        
        # Statistics text area
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setFont(FontHelper.get_monospace_font(9))
        layout.addWidget(self.stats_text)
    
    def display_statistics(self, stats: DocumentStats):
        """Display document statistics."""
        text = self.format_statistics(stats)
        self.stats_text.setPlainText(text)
    
    def format_statistics(self, stats: DocumentStats) -> str:
        """Format statistics for display."""
        text = "Document Collection Statistics\n"
        text += "=" * 50 + "\n\n"
        
        # Basic info
        text += f"Total Documents: {format_number(stats.total_count)}\n"
        text += f"Unique Fields: {len(stats.unique_fields)}\n"
        text += f"Common Fields: {len(stats.common_fields)}\n"
        if stats.avg_document_size > 0:
            text += f"Average Document Size: {format_bytes(int(stats.avg_document_size))}\n"
        text += "\n"
        
        # Field frequency
        text += "Field Frequency:\n"
        text += "-" * 30 + "\n"
        most_common = stats.get_most_common_fields(20)
        for field, count in most_common:
            percentage = stats.get_field_coverage(field)
            text += f"{field:25} {count:>6} ({percentage:>5.1f}%)\n"
        text += "\n"
        
        # Field types
        text += "Field Types:\n"
        text += "-" * 30 + "\n"
        for field in sorted(stats.field_types.keys())[:20]:
            text += f"{field}:\n"
            for type_name, count in stats.field_types[field].items():
                text += f"  {type_name:15} {count:>6}\n"
        text += "\n"
        
        # Sample values
        text += "Sample Values:\n"
        text += "-" * 30 + "\n"
        for field in sorted(stats.sample_values.keys())[:15]:
            values = stats.sample_values[field][:5]
            if values:
                text += f"{field:20} {', '.join(values)}\n"
        
        return text


class DocumentViewer(QWidget):
    """
    Comprehensive document viewer with multiple visualization modes.
    
    Provides JSON view, table view, tree view, and statistics for MongoDB documents.
    """
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.logger = get_logger(__name__)
        self.current_documents = []
        self.current_stats = None
        self.current_database = None
        self.current_collection = None
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the document viewer UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Use a splitter to control space allocation
        splitter = QSplitter(Qt.Vertical)
        
        # Header with collection info and query widget (compact)
        self.create_header_section(splitter)
        
        # Main content with tabs (gets most of the space)
        self.create_content_tabs(splitter)
        
        # Set splitter proportions: 25% for header/query, 75% for documents
        splitter.setSizes([200, 600])  # Header gets 200px, documents get 600px
        splitter.setStretchFactor(0, 0)  # Header doesn't stretch
        splitter.setStretchFactor(1, 1)  # Documents area stretches
        
        layout.addWidget(splitter)
    
    def create_header_section(self, parent_splitter):
        """Create the header section with collection info and query controls."""
        header_group = QGroupBox("Collection & Query")
        header_group.setMaximumHeight(180)  # Limit header height
        header_layout = QVBoxLayout(header_group)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(8)
        
        # Collection info (more compact)
        info_layout = QHBoxLayout()
        
        collection_info = QLabel("No collection selected")
        collection_info.setStyleSheet("font-weight: bold; color: #1976d2; margin-right: 15px;")
        self.collection_label = collection_info
        info_layout.addWidget(QLabel("Collection:"))
        info_layout.addWidget(collection_info)
        
        info_layout.addStretch()
        
        count_info = QLabel("0 documents")
        count_info.setStyleSheet("color: #666;")
        self.count_label = count_info
        info_layout.addWidget(QLabel("Count:"))
        info_layout.addWidget(count_info)
        
        header_layout.addLayout(info_layout)
        
        # Query widget (compact version)
        self.query_widget = QueryWidget()
        self.query_widget.setMaximumHeight(120)  # Limit query widget height
        header_layout.addWidget(self.query_widget)
        
        parent_splitter.addWidget(header_group)
    
    def create_content_tabs(self, parent_splitter):
        """Create the main content area with tabs."""
        self.tab_widget = QTabWidget()
        
        # JSON view tab
        self.create_json_tab()
        
        # Table view tab
        self.create_table_tab()
        
        # Tree view tab
        self.create_tree_tab()
        
        # Statistics tab
        self.create_statistics_tab()
        
        parent_splitter.addWidget(self.tab_widget)
    
    def create_json_tab(self):
        """Create the JSON view tab with MongoDB Compass-like design."""
        # Create main widget with scroll area
        from PyQt5.QtWidgets import QScrollArea, QVBoxLayout as QVBox
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container for documents
        self.documents_container = QWidget()
        self.documents_layout = QVBox(self.documents_container)
        self.documents_layout.setSpacing(10)
        self.documents_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add stretch at the end to push documents to top
        self.documents_layout.addStretch()
        
        scroll_area.setWidget(self.documents_container)
        self.tab_widget.addTab(scroll_area, "Documents")
        
        # Store reference for updates
        self.json_scroll_area = scroll_area
    
    def create_table_tab(self):
        """Create the table view tab."""
        self.table_widget = DocumentTableWidget()
        self.tab_widget.addTab(self.table_widget, "Table View")
    
    def create_tree_tab(self):
        """Create the tree view tab."""
        self.tree_widget = DocumentTreeWidget()
        self.tab_widget.addTab(self.tree_widget, "Tree View")
    
    def create_statistics_tab(self):
        """Create the statistics tab."""
        self.statistics_widget = StatisticsWidget()
        self.tab_widget.addTab(self.statistics_widget, "Statistics")
    
    def setup_connections(self):
        """Setup signal connections."""
        self.query_widget.query_requested.connect(self.execute_query)
    
    def display_documents(self, documents: List[Dict[str, Any]], 
                         database: str, collection: str, stats: DocumentStats):
        """
        Display documents in all views.
        
        Args:
            documents: List of documents to display
            database: Database name
            collection: Collection name
            stats: Document statistics
        """
        self.current_documents = documents
        self.current_stats = stats
        self.current_database = database
        self.current_collection = collection
        
        # Update header
        self.collection_label.setText(f"{database}.{collection}")
        document_count = len(documents)
        if document_count == 1:
            self.count_label.setText(f"{format_number(document_count)} document")
        else:
            self.count_label.setText(f"{format_number(document_count)} documents")
        
        # Update all views
        self.update_json_view(documents)
        self.update_table_view(documents)
        self.update_tree_view(documents)
        self.update_statistics_view(stats)
        
        self.logger.info(f"Displayed {len(documents)} documents from {database}.{collection}")
    
    def update_json_view(self, documents: List[Dict[str, Any]]):
        """Update the JSON view with MongoDB Compass-like document cards."""
        # Clear existing documents
        self.clear_documents_container()
        
        if not documents:
            self.add_no_documents_message()
            return
        
        # Add summary header
        self.add_documents_summary(len(documents))
        
        try:
            # Add each document as a separate card
            for i, doc in enumerate(documents):
                doc_card = self.create_document_card(doc, i)
                self.documents_layout.insertWidget(self.documents_layout.count() - 1, doc_card)
        except Exception as e:
            self.add_error_message(f"Error displaying documents: {str(e)}")
            self.logger.error(f"Error updating JSON view: {e}")
    
    def add_documents_summary(self, count: int):
        """Add a summary header showing document count."""
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 10px;
            }
        """)
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(10, 8, 10, 8)
        
        # Document count
        count_text = "document" if count == 1 else "documents"
        summary_label = QLabel(f"Showing {count} {count_text}")
        summary_label.setStyleSheet("""
            color: #495057;
            font-weight: 500;
            font-size: 13px;
        """)
        summary_layout.addWidget(summary_label)
        
        summary_layout.addStretch()
        
        # Add actions (future: export, refresh, etc.)
        actions_label = QLabel("💡 Click copy icon to copy individual documents")
        actions_label.setStyleSheet("""
            color: #6c757d;
            font-size: 11px;
            font-style: italic;
        """)
        summary_layout.addWidget(actions_label)
        
        self.documents_layout.insertWidget(0, summary_frame)
    
    def clear_documents_container(self):
        """Clear all document cards from the container."""
        # Remove all widgets except the stretch at the end
        while self.documents_layout.count() > 1:
            child = self.documents_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def add_no_documents_message(self):
        """Add a message when no documents are available."""
        message_frame = QFrame()
        message_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        message_layout = QVBoxLayout(message_frame)
        
        message_label = QLabel("No documents to display")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("color: #666; font-size: 16px; font-weight: bold;")
        message_layout.addWidget(message_label)
        
        self.documents_layout.insertWidget(0, message_frame)
    
    def add_error_message(self, error_text: str):
        """Add an error message card."""
        error_frame = QFrame()
        error_frame.setStyleSheet("""
            QFrame {
                background-color: #ffebee;
                border: 1px solid #f44336;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        error_layout = QVBoxLayout(error_frame)
        
        error_label = QLabel(error_text)
        error_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        error_layout.addWidget(error_label)
        
        self.documents_layout.insertWidget(0, error_frame)
    
    def create_document_card(self, document: Dict[str, Any], index: int) -> QFrame:
        """Create a MongoDB Compass-style document card."""
        # Main card frame
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #1976d2;
                background-color: #fafafa;
            }
        """)
        card.setContentsMargins(0, 0, 0, 0)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(8)
        
        # Header with document index and _id
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Document number
        doc_number = QLabel(f"Document {index + 1}")
        doc_number.setStyleSheet("""
            font-weight: bold;
            color: #1976d2;
            font-size: 14px;
        """)
        header_layout.addWidget(doc_number)
        
        # Object ID (if present)
        if '_id' in document:
            id_label = QLabel(f"ObjectId: {str(document['_id'])}")
            id_label.setStyleSheet("""
                color: #666;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            """)
            header_layout.addWidget(id_label)
        
        header_layout.addStretch()
        
        # Copy button
        copy_btn = QPushButton()
        copy_btn.setIcon(qta.icon('fa5s.copy', color='#666'))
        copy_btn.setToolTip("Copy document to clipboard")
        copy_btn.setFixedSize(24, 24)
        copy_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        copy_btn.clicked.connect(lambda: self.copy_document_to_clipboard(document))
        header_layout.addWidget(copy_btn)
        
        # Edit button
        edit_btn = QPushButton()
        edit_btn.setIcon(qta.icon('fa5s.edit', color='#666'))
        edit_btn.setToolTip("Edit document")
        edit_btn.setFixedSize(24, 24)
        edit_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        header_layout.addWidget(edit_btn)
        
        # Expand/Collapse button
        expand_btn = QPushButton()
        expand_btn.setIcon(qta.icon('fa5s.chevron-up', color='#666'))
        expand_btn.setToolTip("Collapse document")
        expand_btn.setFixedSize(24, 24)
        expand_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f5f5f5;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        header_layout.addWidget(expand_btn)
        
        card_layout.addLayout(header_layout)
        
        # Edit action buttons (initially hidden)
        edit_actions_layout = QHBoxLayout()
        edit_actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setIcon(qta.icon('fa5s.save', color='white'))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        edit_actions_layout.addWidget(save_btn)
        
        # Cancel button  
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(qta.icon('fa5s.times', color='white'))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        edit_actions_layout.addWidget(cancel_btn)
        
        edit_actions_layout.addStretch()
        
        edit_actions_widget = QWidget()
        edit_actions_widget.setLayout(edit_actions_layout)
        edit_actions_widget.hide()
        card_layout.addWidget(edit_actions_widget)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("border: none; background-color: #e0e0e0; height: 1px;")
        card_layout.addWidget(separator)
        
        # Document content
        content_text = QTextEdit()
        content_text.setReadOnly(True)  # Start in read-only mode
        content_text.setFont(FontHelper.get_monospace_font(11))
        
        # Remove scrollbars and auto-size to content
        content_text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_text.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Store original document for cancel operation
        content_text.original_document = document
        content_text.is_editing = False
        
        # Format the document nicely
        formatted_json = self.format_document_for_display(document)
        content_text.setPlainText(formatted_json)
        
        # Auto-resize to content height
        content_text.document().documentLayout().documentSizeChanged.connect(
            lambda: self.resize_text_edit_to_content(content_text)
        )
        
        # Initial resize
        self.resize_text_edit_to_content(content_text)
        
        # Add syntax highlighting
        highlighter = JsonSyntaxHighlighter(content_text.document())
        
        # Style the text area
        content_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #fafafa;
                padding: 8px;
                color: #333;
            }
            QTextEdit:focus {
                border-color: #2196f3;
            }
            QTextEdit[readOnly="false"] {
                background-color: #ffffff;
                border: 2px solid #ff9800;
            }
        """)
        
        # Connect expand/collapse functionality
        def toggle_expand():
            if content_text.isVisible():
                content_text.hide()
                expand_btn.setIcon(qta.icon('fa5s.chevron-down', color='#666'))
                expand_btn.setToolTip("Expand document")
            else:
                content_text.show()
                expand_btn.setIcon(qta.icon('fa5s.chevron-up', color='#666'))
                expand_btn.setToolTip("Collapse document")
        
        expand_btn.clicked.connect(toggle_expand)
        
        # Edit mode functionality
        def toggle_edit_mode():
            if content_text.is_editing:
                # Already in edit mode, this shouldn't happen as edit button is hidden
                return
            else:
                # Enter edit mode
                content_text.setReadOnly(False)
                content_text.is_editing = True
                content_text.setStyleSheet(content_text.styleSheet() + """
                    QTextEdit {
                        background-color: #ffffff !important;
                        border: 2px solid #ff9800 !important;
                    }
                """)
                
                # Show edit action buttons
                edit_actions_widget.show()
                save_btn.show()
                cancel_btn.show()
                
                # Hide regular buttons 
                copy_btn.hide()
                edit_btn.hide()
                expand_btn.hide()
        
        def save_document():
            try:
                # Parse the JSON to validate it
                new_content = content_text.toPlainText()
                parsed_doc = json.loads(new_content)
                
                # Get the document ID from the original document
                original_doc = content_text.original_document
                if '_id' not in original_doc:
                    QMessageBox.warning(self, "Error", "Cannot update document: No _id field found")
                    return
                
                document_id = str(original_doc['_id'])
                
                # Check if we have database and collection info
                if not self.current_database or not self.current_collection:
                    QMessageBox.warning(self, "Error", "No database or collection selected")
                    return
                
                # Perform the update through the controller
                success = self.controller.update_document(
                    self.current_database,
                    self.current_collection, 
                    document_id,
                    parsed_doc
                )
                
                if success:
                    # Update the stored original document
                    content_text.original_document = parsed_doc.copy()
                    if '_id' not in content_text.original_document:
                        content_text.original_document['_id'] = original_doc['_id']
                    
                    exit_edit_mode()
                    QMessageBox.information(self, "Success", "Document updated successfully!")
                else:
                    QMessageBox.warning(self, "Update Failed", "Document could not be updated. It may have been deleted or modified by another user.")
                
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Invalid JSON", f"Invalid JSON format:\n{str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save document:\n{str(e)}")
        
        def cancel_edit():
            # Restore original content
            formatted_json = self.format_document_for_display(content_text.original_document)
            content_text.setPlainText(formatted_json)
            exit_edit_mode()
        
        def exit_edit_mode():
            # Exit edit mode
            content_text.setReadOnly(True)
            content_text.is_editing = False
            content_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    background-color: #fafafa;
                    padding: 8px;
                    color: #333;
                }
                QTextEdit:focus {
                    border-color: #2196f3;
                }
            """)
            
            # Hide edit action buttons
            edit_actions_widget.hide()
            save_btn.hide()
            cancel_btn.hide()
            
            # Show regular buttons
            copy_btn.show()
            edit_btn.show()
            expand_btn.show()
        
        # Connect button functionality
        edit_btn.clicked.connect(toggle_edit_mode)
        save_btn.clicked.connect(save_document)
        cancel_btn.clicked.connect(cancel_edit)
        
        card_layout.addWidget(content_text)
        
        return card
    
    def resize_text_edit_to_content(self, text_edit: QTextEdit):
        """Resize QTextEdit to fit its content without scrollbars."""
        try:
            doc = text_edit.document()
            doc.setTextWidth(text_edit.viewport().width())
            
            # Calculate required height
            height = doc.size().height()
            
            # Add padding for borders and margins
            height += 20
            
            # Set reasonable limits
            min_height = 60   # Minimum height for very small documents
            max_height = 400  # Maximum height to prevent huge documents
            
            height = max(min_height, min(height, max_height))
            
            text_edit.setFixedHeight(int(height))
        except Exception as e:
            # Fallback to a default height if calculation fails
            text_edit.setFixedHeight(120)
    
    def format_document_for_display(self, document: Dict[str, Any]) -> str:
        """Format a document for display in a card."""
        try:
            # Remove _id from display if it's an ObjectId (already shown in header)
            display_doc = document.copy()
            if '_id' in display_doc:
                # Keep _id for reference but format it nicely
                if hasattr(display_doc['_id'], '__str__'):
                    display_doc['_id'] = f"ObjectId('{display_doc['_id']}')"
            
            # Pretty print with proper indentation
            formatted = json.dumps(display_doc, indent=2, default=str, ensure_ascii=False)
            return formatted
        except Exception as e:
            return f"Error formatting document: {str(e)}"
    
    def copy_document_to_clipboard(self, document: Dict[str, Any]):
        """Copy document to clipboard."""
        try:
            from PyQt5.QtWidgets import QApplication
            formatted = json.dumps(document, indent=2, default=str, ensure_ascii=False)
            clipboard = QApplication.clipboard()
            clipboard.setText(formatted)
            self.logger.info("Document copied to clipboard")
        except Exception as e:
            self.logger.error(f"Failed to copy document: {e}")
    
    def update_table_view(self, documents: List[Dict[str, Any]]):
        """Update the table view."""
        self.table_widget.populate_documents(documents)
    
    def update_tree_view(self, documents: List[Dict[str, Any]]):
        """Update the tree view."""
        # Limit tree view to first 10 documents for performance
        display_docs = documents[:10] if len(documents) > 10 else documents
        self.tree_widget.populate_documents(display_docs)
        
        if len(documents) > 10:
            self.logger.info("Tree view limited to first 10 documents for performance")
    
    def update_statistics_view(self, stats: DocumentStats):
        """Update the statistics view."""
        self.statistics_widget.display_statistics(stats)
    
    @pyqtSlot(dict, str)
    def execute_query(self, query: Dict[str, Any], query_type: str):
        """Execute a custom query."""
        if not self.current_database or not self.current_collection:
            self.logger.warning("No collection selected for query execution")
            return
        
        # Convert string to enum
        query_type_enum = QueryType.FIND
        if query_type == "count":
            query_type_enum = QueryType.COUNT
        elif query_type == "distinct":
            query_type_enum = QueryType.DISTINCT
        elif query_type == "aggregate":
            query_type_enum = QueryType.AGGREGATE
        
        # Execute query through controller
        self.controller.execute_custom_query(
            self.current_database,
            self.current_collection,
            query,
            query_type_enum,
            self.query_widget.get_limit(),
            self.query_widget.get_skip()
        )
    
    def clear(self):
        """Clear all views."""
        self.current_documents = []
        self.current_stats = None
        self.current_database = None
        self.current_collection = None
        
        self.collection_label.setText("No collection selected")
        self.count_label.setText("0 documents")
        
        self.json_text.clear()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(0)
        self.tree_widget.clear()
        self.statistics_widget.stats_text.clear()
        
        self.query_widget.clear_query()
