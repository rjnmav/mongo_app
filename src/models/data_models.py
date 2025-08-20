"""
Data models for the MongoDB Visualizer application.

This module defines the core data structures and models used throughout
the application, providing type safety and data validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
import json


class ConnectionStatus(Enum):
    """Database connection status enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


class DocumentFormat(Enum):
    """Document display format enumeration."""
    JSON = "json"
    TABLE = "table"
    TREE = "tree"


class QueryType(Enum):
    """Query type enumeration."""
    FIND = "find"
    AGGREGATE = "aggregate"
    COUNT = "count"
    DISTINCT = "distinct"


@dataclass
class ConnectionInfo:
    """Database connection information."""
    name: str = ""
    host: str = "localhost"
    port: int = 27017
    username: Optional[str] = None
    password: Optional[str] = None
    auth_database: str = "admin"
    auth_enabled: bool = False
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    connection_timeout: int = 5000
    server_selection_timeout: int = 5000
    max_pool_size: int = 50
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding sensitive data."""
        return {
            'name': self.name,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'auth_database': self.auth_database,
            'auth_enabled': self.auth_enabled,
            'ssl_enabled': self.ssl_enabled,
            'connection_timeout': self.connection_timeout,
            'server_selection_timeout': self.server_selection_timeout,
            'max_pool_size': self.max_pool_size
        }
    
    def get_display_name(self) -> str:
        """Get a human-readable display name for the connection."""
        if self.name:
            return f"{self.name} ({self.host}:{self.port})"
        return f"{self.host}:{self.port}"
    
    def get_connection_string(self, include_credentials: bool = True) -> str:
        """Generate MongoDB connection string."""
        if include_credentials and self.auth_enabled and self.username and self.password:
            auth_part = f"{self.username}:{self.password}@"
        else:
            auth_part = ""
        
        base_url = f"mongodb://{auth_part}{self.host}:{self.port}/"
        
        # Add authentication database if needed
        if self.auth_enabled and self.auth_database != "admin":
            base_url += f"{self.auth_database}"
        
        return base_url


@dataclass
class DatabaseInfo:
    """Database information."""
    name: str
    size_on_disk: int = 0
    collection_count: int = 0
    data_size: int = 0
    storage_size: int = 0
    index_count: int = 0
    index_size: int = 0
    created_at: Optional[datetime] = None
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_formatted_size_on_disk(self) -> str:
        """Get formatted size on disk."""
        return self.format_size(self.size_on_disk)
    
    def get_formatted_data_size(self) -> str:
        """Get formatted data size."""
        return self.format_size(self.data_size)


@dataclass
class CollectionInfo:
    """Collection information."""
    name: str
    database: str
    document_count: int = 0
    data_size: int = 0
    storage_size: int = 0
    index_count: int = 0
    index_size: int = 0
    avg_document_size: float = 0.0
    capped: bool = False
    max_size: Optional[int] = None
    max_documents: Optional[int] = None
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_full_name(self) -> str:
        """Get full collection name including database."""
        return f"{self.database}.{self.name}"
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_formatted_data_size(self) -> str:
        """Get formatted data size."""
        return self.format_size(self.data_size)


@dataclass
class QueryInfo:
    """Query information and execution details."""
    query: Dict[str, Any]
    query_type: QueryType = QueryType.FIND
    database: str = ""
    collection: str = ""
    limit: int = 100
    skip: int = 0
    sort: Optional[Dict[str, Any]] = None
    projection: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    result_count: Optional[int] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'query': self.query,
            'query_type': self.query_type.value,
            'database': self.database,
            'collection': self.collection,
            'limit': self.limit,
            'skip': self.skip,
            'sort': self.sort,
            'projection': self.projection,
            'execution_time': self.execution_time,
            'result_count': self.result_count,
            'error': self.error,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }
    
    def get_query_string(self) -> str:
        """Get formatted query string."""
        return json.dumps(self.query, indent=2, default=str)


@dataclass
class DocumentStats:
    """Statistics for a set of documents."""
    total_count: int = 0
    field_frequency: Dict[str, int] = field(default_factory=dict)
    field_types: Dict[str, Dict[str, int]] = field(default_factory=dict)
    sample_values: Dict[str, List[str]] = field(default_factory=dict)
    unique_fields: List[str] = field(default_factory=list)
    common_fields: List[str] = field(default_factory=list)
    avg_document_size: float = 0.0
    min_document_size: int = 0
    max_document_size: int = 0
    
    def get_field_coverage(self, field_name: str) -> float:
        """Get field coverage percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.field_frequency.get(field_name, 0) / self.total_count) * 100
    
    def get_most_common_fields(self, limit: int = 10) -> List[tuple]:
        """Get most common fields with their frequencies."""
        return sorted(self.field_frequency.items(), key=lambda x: x[1], reverse=True)[:limit]


@dataclass
class ApplicationState:
    """Current application state."""
    connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    current_connection: Optional[ConnectionInfo] = None
    current_database: Optional[str] = None
    current_collection: Optional[str] = None
    document_format: DocumentFormat = DocumentFormat.JSON
    query_limit: int = 100
    query_skip: int = 0
    auto_refresh: bool = False
    last_query: Optional[QueryInfo] = None
    
    def is_connected(self) -> bool:
        """Check if currently connected to a database."""
        return self.connection_status == ConnectionStatus.CONNECTED
    
    def has_selection(self) -> bool:
        """Check if a database and collection are selected."""
        return bool(self.current_database and self.current_collection)


@dataclass
class ErrorInfo:
    """Error information for logging and display."""
    message: str
    error_type: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'message': self.message,
            'error_type': self.error_type,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'stack_trace': self.stack_trace
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    memory_usage: Optional[int] = None
    cpu_usage: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    
    def mark_completed(self) -> None:
        """Mark the operation as completed."""
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    def mark_failed(self, error: str) -> None:
        """Mark the operation as failed."""
        self.success = False
        self.error = error
        self.mark_completed()


# Type aliases for better code readability
DocumentList = List[Dict[str, Any]]
IndexList = List[Dict[str, Any]]
QueryResult = Union[DocumentList, int, List[str]]  # find, count, or distinct results
