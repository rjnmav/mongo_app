"""
Database controller for the MongoDB Visualizer application.

This module provides the main controller layer that coordinates between
the UI and the data models, implementing business logic and orchestrating
database operations.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime
import json
import logging

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer

from ..models.data_models import (
    ConnectionInfo, DatabaseInfo, CollectionInfo, QueryInfo, QueryType,
    ConnectionStatus, DocumentList, DocumentStats, ApplicationState,
    ErrorInfo, PerformanceMetrics
)
from ..models.mongodb_connection import MongoDBConnection, ConnectionPool
from ..utils.logging_config import get_logger, PerformanceTimer


class DatabaseWorker(QThread):
    """Worker thread for database operations to keep UI responsive."""
    
    # Signals for communication with main thread
    operation_completed = pyqtSignal(str, object)  # operation_name, result
    operation_failed = pyqtSignal(str, str)  # operation_name, error_message
    progress_updated = pyqtSignal(str, int)  # message, percentage
    
    def __init__(self, connection: MongoDBConnection):
        super().__init__()
        self.connection = connection
        self.operation_queue = []
        self.current_operation = None
        self.logger = get_logger(__name__)
    
    def add_operation(self, operation_name: str, operation_func: Callable, *args, **kwargs):
        """Add an operation to the queue."""
        self.operation_queue.append((operation_name, operation_func, args, kwargs))
        if not self.isRunning():
            self.start()
    
    def run(self):
        """Execute queued operations."""
        while self.operation_queue:
            operation_name, operation_func, args, kwargs = self.operation_queue.pop(0)
            self.current_operation = operation_name
            
            try:
                self.logger.debug(f"Executing operation: {operation_name}")
                result = operation_func(*args, **kwargs)
                self.operation_completed.emit(operation_name, result)
                
            except Exception as e:
                error_msg = f"Operation {operation_name} failed: {str(e)}"
                self.logger.error(error_msg)
                self.operation_failed.emit(operation_name, error_msg)
            
            finally:
                self.current_operation = None


class DatabaseController(QObject):
    """
    Main controller for database operations and state management.
    
    Provides a high-level interface for the UI to interact with MongoDB,
    handles connection management, query execution, and data analysis.
    """
    
    # Signals for UI updates
    connection_status_changed = pyqtSignal(ConnectionStatus)
    databases_loaded = pyqtSignal(list)  # List[DatabaseInfo]
    collections_loaded = pyqtSignal(str, list)  # database_name, List[CollectionInfo]
    documents_loaded = pyqtSignal(str, str, list, DocumentStats)  # db, collection, documents, stats
    query_executed = pyqtSignal(QueryInfo)
    error_occurred = pyqtSignal(ErrorInfo)
    performance_updated = pyqtSignal(PerformanceMetrics)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self.connection_pool = ConnectionPool()
        self.connection = MongoDBConnection(self.connection_pool)
        self.worker = DatabaseWorker(self.connection)
        self.state = ApplicationState()
        self.logger = get_logger(__name__)
        
        # Performance monitoring
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self._auto_refresh)
        
        # Connect worker signals
        self.worker.operation_completed.connect(self._handle_operation_completed)
        self.worker.operation_failed.connect(self._handle_operation_failed)
        
        # Initialize recent connections
        self.recent_connections: List[ConnectionInfo] = []
        if config:
            self.recent_connections = self._load_recent_connections()
    
    def connect_to_database(self, connection_info: ConnectionInfo) -> None:
        """
        Connect to a MongoDB database.
        
        Args:
            connection_info: Database connection parameters
        """
        with PerformanceTimer("database_connection", self.logger):
            self.state.connection_status = ConnectionStatus.CONNECTING
            self.connection_status_changed.emit(self.state.connection_status)
            
            # Use worker thread for connection
            self.worker.add_operation(
                "connect",
                self.connection.connect,
                connection_info
            )
    
    def disconnect_from_database(self) -> None:
        """Disconnect from the current database."""
        try:
            self.connection.disconnect()
            self.state.connection_status = ConnectionStatus.DISCONNECTED
            self.state.current_connection = None
            self.state.current_database = None
            self.state.current_collection = None
            
            # Stop auto-refresh
            self.auto_refresh_timer.stop()
            
            self.connection_status_changed.emit(self.state.connection_status)
            self.logger.info("Disconnected from database")
            
        except Exception as e:
            self._emit_error("Disconnect failed", e)
    
    def load_databases(self) -> None:
        """Load list of databases from the connected MongoDB instance."""
        if not self.connection.is_connected():
            self._emit_error("Load databases failed", "Not connected to database")
            return
        
        self.worker.add_operation("load_databases", self.connection.get_databases)
    
    def load_collections(self, database_name: str) -> None:
        """
        Load collections for a specific database.
        
        Args:
            database_name: Name of the database
        """
        if not self.connection.is_connected():
            self._emit_error("Load collections failed", "Not connected to database")
            return
        
        self.state.current_database = database_name
        self.worker.add_operation(
            "load_collections",
            self.connection.get_collections,
            database_name
        )
    
    def load_documents(self, database_name: str, collection_name: str, 
                      limit: int = None, skip: int = None, 
                      query: Dict[str, Any] = None) -> None:
        """
        Load documents from a collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            limit: Maximum number of documents to load
            skip: Number of documents to skip
            query: MongoDB query filter
        """
        if not self.connection.is_connected():
            self._emit_error("Load documents failed", "Not connected to database")
            return
        
        # Set current selection
        self.state.current_database = database_name
        self.state.current_collection = collection_name
        
        # Use configured limits if not provided
        if limit is None:
            limit = self.state.query_limit
        if skip is None:
            skip = self.state.query_skip
        if query is None:
            query = {}
        
        # Create query info
        query_info = QueryInfo(
            query=query,
            query_type=QueryType.FIND,
            database=database_name,
            collection=collection_name,
            limit=limit,
            skip=skip
        )
        
        self.worker.add_operation(
            "load_documents",
            self._execute_load_documents,
            query_info
        )
    
    def execute_custom_query(self, database_name: str, collection_name: str,
                           query: Dict[str, Any], query_type: QueryType = QueryType.FIND,
                           limit: int = None, skip: int = None) -> None:
        """
        Execute a custom MongoDB query.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            query: MongoDB query
            query_type: Type of query to execute
            limit: Maximum number of documents
            skip: Number of documents to skip
        """
        if not self.connection.is_connected():
            self._emit_error("Query execution failed", "Not connected to database")
            return
        
        # Use configured limits if not provided
        if limit is None:
            limit = self.state.query_limit
        if skip is None:
            skip = self.state.query_skip
        
        query_info = QueryInfo(
            query=query,
            query_type=query_type,
            database=database_name,
            collection=collection_name,
            limit=limit,
            skip=skip
        )
        
        self.worker.add_operation(
            "execute_query",
            self.connection.execute_query,
            query_info
        )
    
    def test_connection(self, connection_info: ConnectionInfo) -> bool:
        """
        Test a database connection without storing it.
        
        Args:
            connection_info: Connection parameters to test
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create temporary connection
            test_connection = MongoDBConnection()
            result = test_connection.connect(connection_info)
            test_connection.disconnect()
            return result
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def update_document(self, database_name: str, collection_name: str,
                       document_id: str, updated_document: Dict[str, Any]) -> bool:
        """
        Update a document in the specified collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection  
            document_id: ID of the document to update
            updated_document: The complete updated document
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            self._emit_error("Update document failed", "Not connected to database")
            return False
        
        try:
            # Perform update through connection
            success = self.connection.update_document(
                database_name, collection_name, document_id, updated_document
            )
            
            if success:
                self.logger.info(f"Document updated successfully in {database_name}.{collection_name}")
                # Optionally reload documents to reflect changes
                # self.load_documents(database_name, collection_name)
            else:
                self.logger.warning(f"Document update failed - no matching document found")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Document update failed: {e}")
            self._emit_error("Update document failed", str(e))
            return False
    
    def get_query_history(self) -> List[QueryInfo]:
        """Get the query execution history."""
        return self.connection.get_query_history()
    
    def get_performance_metrics(self) -> List[PerformanceMetrics]:
        """Get performance metrics for database operations."""
        return self.connection.get_performance_metrics()
    
    def clear_history(self) -> None:
        """Clear query history and performance metrics."""
        self.connection.clear_history()
    
    def set_auto_refresh(self, enabled: bool, interval_seconds: int = 30) -> None:
        """
        Enable or disable auto-refresh of current view.
        
        Args:
            enabled: Whether to enable auto-refresh
            interval_seconds: Refresh interval in seconds
        """
        self.state.auto_refresh = enabled
        
        if enabled and self.connection.is_connected():
            self.auto_refresh_timer.start(interval_seconds * 1000)
        else:
            self.auto_refresh_timer.stop()
    
    def export_data(self, format_type: str, data: Any, file_path: str) -> None:
        """
        Export data to a file.
        
        Args:
            format_type: Export format ('json', 'csv')
            data: Data to export
            file_path: Target file path
        """
        self.worker.add_operation(
            "export_data",
            self._export_data,
            format_type, data, file_path
        )
    
    def get_application_state(self) -> ApplicationState:
        """Get the current application state."""
        return self.state
    
    def save_recent_connection(self, connection_info: ConnectionInfo) -> None:
        """Save a connection to recent connections list."""
        # Remove existing connection with same host:port
        self.recent_connections = [
            conn for conn in self.recent_connections 
            if not (conn.host == connection_info.host and conn.port == connection_info.port)
        ]
        
        # Add to beginning of list
        self.recent_connections.insert(0, connection_info)
        
        # Keep only last 10 connections
        self.recent_connections = self.recent_connections[:10]
        
        # Save to config if available
        if self.config:
            self.config.save_recent_connection(connection_info.to_dict())
    
    def get_recent_connections(self) -> List[ConnectionInfo]:
        """Get list of recent connections."""
        return self.recent_connections.copy()
    
    # Private methods
    
    def _execute_load_documents(self, query_info: QueryInfo) -> Tuple[DocumentList, DocumentStats]:
        """Execute document loading and generate statistics."""
        result, updated_query = self.connection.execute_query(query_info)
        
        # Generate document statistics
        stats = self._analyze_documents(result)
        
        return result, stats
    
    def _analyze_documents(self, documents: DocumentList) -> DocumentStats:
        """
        Analyze a list of documents and generate statistics.
        
        Args:
            documents: List of documents to analyze
            
        Returns:
            DocumentStats object with analysis results
        """
        if not documents:
            return DocumentStats()
        
        stats = DocumentStats(total_count=len(documents))
        
        # Analyze each document
        document_sizes = []
        
        for doc in documents:
            # Calculate document size (rough estimate)
            doc_size = len(str(doc))
            document_sizes.append(doc_size)
            
            # Analyze fields
            for field_name, field_value in doc.items():
                # Field frequency
                stats.field_frequency[field_name] = stats.field_frequency.get(field_name, 0) + 1
                
                # Field types
                field_type = type(field_value).__name__
                if field_name not in stats.field_types:
                    stats.field_types[field_name] = {}
                stats.field_types[field_name][field_type] = \
                    stats.field_types[field_name].get(field_type, 0) + 1
                
                # Sample values
                if field_name not in stats.sample_values:
                    stats.sample_values[field_name] = []
                
                if len(stats.sample_values[field_name]) < 5:
                    if isinstance(field_value, (str, int, float, bool)) and field_value not in stats.sample_values[field_name]:
                        stats.sample_values[field_name].append(str(field_value))
        
        # Calculate size statistics
        if document_sizes:
            stats.avg_document_size = sum(document_sizes) / len(document_sizes)
            stats.min_document_size = min(document_sizes)
            stats.max_document_size = max(document_sizes)
        
        # Identify common and unique fields
        total_docs = len(documents)
        stats.unique_fields = [field for field, count in stats.field_frequency.items() if count == 1]
        stats.common_fields = [field for field, count in stats.field_frequency.items() if count == total_docs]
        
        return stats
    
    def _export_data(self, format_type: str, data: Any, file_path: str) -> None:
        """Export data to file in specified format."""
        try:
            if format_type.lower() == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
            elif format_type.lower() == 'csv':
                import csv
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
                else:
                    raise ValueError("CSV export requires list of dictionaries")
            
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            
            self.logger.info(f"Data exported to {file_path}")
            
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")
    
    def _auto_refresh(self) -> None:
        """Auto-refresh current view."""
        if (self.state.has_selection() and 
            self.connection.is_connected() and 
            self.state.auto_refresh):
            
            self.load_documents(
                self.state.current_database,
                self.state.current_collection,
                self.state.query_limit,
                self.state.query_skip
            )
    
    def _handle_operation_completed(self, operation_name: str, result: Any) -> None:
        """Handle completed worker operations."""
        try:
            if operation_name == "connect":
                if result:
                    self.state.connection_status = ConnectionStatus.CONNECTED
                    self.state.current_connection = self.connection.current_connection
                    
                    # Save to recent connections
                    if self.state.current_connection:
                        self.save_recent_connection(self.state.current_connection)
                    
                    self.connection_status_changed.emit(self.state.connection_status)
                    self.logger.info("Connected to database successfully")
                    
                    # Auto-load databases
                    self.load_databases()
                else:
                    self.state.connection_status = ConnectionStatus.ERROR
                    self.connection_status_changed.emit(self.state.connection_status)
            
            elif operation_name == "load_databases":
                self.databases_loaded.emit(result)
            
            elif operation_name == "load_collections":
                self.collections_loaded.emit(self.state.current_database, result)
            
            elif operation_name == "load_documents":
                documents, stats = result
                self.documents_loaded.emit(
                    self.state.current_database,
                    self.state.current_collection,
                    documents,
                    stats
                )
            
            elif operation_name == "execute_query":
                result_data, query_info = result
                self.state.last_query = query_info
                self.query_executed.emit(query_info)
                
                # If it's a find query, also emit documents_loaded
                if query_info.query_type == QueryType.FIND:
                    stats = self._analyze_documents(result_data)
                    self.documents_loaded.emit(
                        query_info.database,
                        query_info.collection,
                        result_data,
                        stats
                    )
            
            elif operation_name == "export_data":
                self.logger.info("Data export completed successfully")
            
        except Exception as e:
            self._emit_error(f"{operation_name} result processing failed", e)
    
    def _handle_operation_failed(self, operation_name: str, error_message: str) -> None:
        """Handle failed worker operations."""
        if operation_name == "connect":
            self.state.connection_status = ConnectionStatus.ERROR
            self.connection_status_changed.emit(self.state.connection_status)
        
        self._emit_error(f"{operation_name} failed", error_message)
    
    def _emit_error(self, message: str, error: Any) -> None:
        """Emit an error signal with proper error information."""
        error_info = ErrorInfo(
            message=message,
            error_type=type(error).__name__ if isinstance(error, Exception) else "Error",
            timestamp=datetime.now(),
            context={
                'current_database': self.state.current_database,
                'current_collection': self.state.current_collection,
                'connection_status': self.state.connection_status.value
            }
        )
        
        self.error_occurred.emit(error_info)
        self.logger.error(f"{message}: {error}")
    
    def _load_recent_connections(self) -> List[ConnectionInfo]:
        """Load recent connections from config."""
        connections = []
        if self.config:
            recent_data = self.config.get_recent_connections()
            for conn_data in recent_data:
                connection_info = ConnectionInfo(
                    name=conn_data.get('name', ''),
                    host=conn_data.get('host', 'localhost'),
                    port=conn_data.get('port', 27017),
                    auth_enabled=conn_data.get('auth_enabled', False),
                    username=conn_data.get('username', ''),
                    auth_database=conn_data.get('auth_db', 'admin')
                )
                connections.append(connection_info)
        return connections
