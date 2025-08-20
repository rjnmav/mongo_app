"""
MongoDB connection and database operations.

This module provides a robust, production-ready MongoDB client with connection
pooling, error handling, retry logic, and comprehensive logging.
"""

import asyncio
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging
import time

from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure, ServerSelectionTimeoutError, OperationFailure,
    ConfigurationError, NetworkTimeout, ExecutionTimeout
)
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId

from .data_models import (
    ConnectionInfo, DatabaseInfo, CollectionInfo, QueryInfo, QueryType,
    ConnectionStatus, DocumentList, QueryResult, PerformanceMetrics, ErrorInfo
)
from ..utils.logging_config import get_logger


class ConnectionPool:
    """
    Connection pool manager for MongoDB connections.
    Handles multiple connections and connection reuse.
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections: Dict[str, MongoClient] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.lock = threading.RLock()
        self.logger = get_logger(__name__)
    
    def get_connection_key(self, conn_info: ConnectionInfo) -> str:
        """Generate a unique key for the connection."""
        return f"{conn_info.host}:{conn_info.port}:{conn_info.auth_database}"
    
    def get_connection(self, conn_info: ConnectionInfo) -> Optional[MongoClient]:
        """Get or create a connection from the pool."""
        key = self.get_connection_key(conn_info)
        
        with self.lock:
            if key in self.connections:
                # Test existing connection
                try:
                    self.connections[key].admin.command('ping')
                    return self.connections[key]
                except Exception:
                    # Connection is stale, remove it
                    self.remove_connection(key)
            
            # Create new connection if pool not full
            if len(self.connections) < self.max_connections:
                client = self._create_client(conn_info)
                if client:
                    self.connections[key] = client
                    self.connection_info[key] = conn_info
                    return client
            
            return None
    
    def remove_connection(self, key: str) -> None:
        """Remove a connection from the pool."""
        with self.lock:
            if key in self.connections:
                try:
                    self.connections[key].close()
                except Exception:
                    pass
                del self.connections[key]
                
            if key in self.connection_info:
                del self.connection_info[key]
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self.lock:
            for client in self.connections.values():
                try:
                    client.close()
                except Exception:
                    pass
            self.connections.clear()
            self.connection_info.clear()
    
    def _create_client(self, conn_info: ConnectionInfo) -> Optional[MongoClient]:
        """Create a new MongoDB client."""
        try:
            # Build client parameters
            client_params = {
                'host': conn_info.host,
                'port': conn_info.port,
                'serverSelectionTimeoutMS': conn_info.server_selection_timeout,
                'connectTimeoutMS': conn_info.connection_timeout,
                'socketTimeoutMS': 30000,
                'maxPoolSize': conn_info.max_pool_size,
            }
            
            # Add authentication parameters only if auth is enabled
            if conn_info.auth_enabled:
                client_params.update({
                    'username': conn_info.username,
                    'password': conn_info.password,
                    'authSource': conn_info.auth_database
                })
            
            # Add SSL parameters if SSL is enabled
            if conn_info.ssl_enabled:
                client_params.update({
                    'ssl': True,
                    'ssl_cert_reqs': 'CERT_NONE'
                })
            
            client = MongoClient(**client_params)
            
            # Test connection
            client.admin.command('ping')
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create MongoDB client: {e}")
            return None


class MongoDBConnection:
    """
    Production-ready MongoDB connection manager.
    
    Provides robust connection handling, query execution, and data retrieval
    with comprehensive error handling and performance monitoring.
    """
    
    def __init__(self, connection_pool: Optional[ConnectionPool] = None):
        self.pool = connection_pool or ConnectionPool()
        self.current_client: Optional[MongoClient] = None
        self.current_connection: Optional[ConnectionInfo] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.logger = get_logger(__name__)
        
        # Performance tracking
        self.query_history: List[QueryInfo] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.max_history_size = 100
    
    async def connect_async(self, connection_info: ConnectionInfo) -> bool:
        """Asynchronously connect to MongoDB."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.connect, connection_info
        )
    
    def connect(self, connection_info: ConnectionInfo) -> bool:
        """
        Connect to MongoDB using the provided connection information.
        
        Args:
            connection_info: Connection parameters
            
        Returns:
            True if connection successful, False otherwise
        """
        metrics = PerformanceMetrics("connect", datetime.now())
        
        try:
            self.status = ConnectionStatus.CONNECTING
            self.logger.info(f"Connecting to MongoDB at {connection_info.host}:{connection_info.port}")
            
            # Get connection from pool
            client = self.pool.get_connection(connection_info)
            if not client:
                raise ConnectionFailure("Could not create connection from pool")
            
            # Test connection with more comprehensive checks
            self._test_connection(client)
            
            # Store connection details
            self.current_client = client
            self.current_connection = connection_info
            self.status = ConnectionStatus.CONNECTED
            
            metrics.mark_completed()
            self.performance_metrics.append(metrics)
            
            self.logger.info(f"Successfully connected to MongoDB")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.status = ConnectionStatus.TIMEOUT
            error_msg = f"Connection timeout: {e}"
            self.logger.error(error_msg)
            metrics.mark_failed(error_msg)
            self.performance_metrics.append(metrics)
            return False
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            error_msg = f"Connection failed: {e}"
            self.logger.error(error_msg)
            metrics.mark_failed(error_msg)
            self.performance_metrics.append(metrics)
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.current_client:
            try:
                # Don't close the client as it's managed by the pool
                self.current_client = None
                self.current_connection = None
                self.status = ConnectionStatus.DISCONNECTED
                self.logger.info("Disconnected from MongoDB")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
    
    def is_connected(self) -> bool:
        """Check if currently connected to MongoDB."""
        if self.status != ConnectionStatus.CONNECTED or not self.current_client:
            return False
        
        try:
            # Quick ping to verify connection
            self.current_client.admin.command('ping')
            return True
        except Exception:
            self.status = ConnectionStatus.ERROR
            return False
    
    def get_databases(self) -> List[DatabaseInfo]:
        """
        Get list of databases with detailed information.
        
        Returns:
            List of DatabaseInfo objects
        """
        if not self.is_connected():
            raise ConnectionFailure("Not connected to MongoDB")
        
        metrics = PerformanceMetrics("get_databases", datetime.now())
        
        try:
            databases = []
            db_names = self.current_client.list_database_names()
            
            for db_name in db_names:
                # Skip system databases
                if db_name in ['admin', 'config', 'local']:
                    continue
                
                try:
                    db_stats = self.current_client[db_name].command('dbStats')
                    db_info = DatabaseInfo(
                        name=db_name,
                        size_on_disk=db_stats.get('storageSize', 0),
                        collection_count=db_stats.get('collections', 0),
                        data_size=db_stats.get('dataSize', 0),
                        storage_size=db_stats.get('storageSize', 0),
                        index_count=db_stats.get('indexes', 0),
                        index_size=db_stats.get('indexSize', 0)
                    )
                    databases.append(db_info)
                except Exception as e:
                    self.logger.warning(f"Could not get stats for database {db_name}: {e}")
                    # Add database with minimal info
                    databases.append(DatabaseInfo(name=db_name))
            
            metrics.mark_completed()
            self.performance_metrics.append(metrics)
            
            return sorted(databases, key=lambda x: x.name)
            
        except Exception as e:
            error_msg = f"Failed to get databases: {e}"
            self.logger.error(error_msg)
            metrics.mark_failed(error_msg)
            self.performance_metrics.append(metrics)
            raise
    
    def get_collections(self, database_name: str) -> List[CollectionInfo]:
        """
        Get list of collections in a database with detailed information.
        
        Args:
            database_name: Name of the database
            
        Returns:
            List of CollectionInfo objects
        """
        if not self.is_connected():
            raise ConnectionFailure("Not connected to MongoDB")
        
        metrics = PerformanceMetrics("get_collections", datetime.now())
        
        try:
            database = self.current_client[database_name]
            collections = []
            
            for coll_name in database.list_collection_names():
                try:
                    collection = database[coll_name]
                    
                    # Get collection stats
                    stats = database.command('collStats', coll_name)
                    
                    # Get indexes
                    indexes = list(collection.list_indexes())
                    
                    coll_info = CollectionInfo(
                        name=coll_name,
                        database=database_name,
                        document_count=stats.get('count', 0),
                        data_size=stats.get('size', 0),
                        storage_size=stats.get('storageSize', 0),
                        index_count=len(indexes),
                        index_size=stats.get('totalIndexSize', 0),
                        avg_document_size=stats.get('avgObjSize', 0),
                        capped=stats.get('capped', False),
                        max_size=stats.get('maxSize'),
                        max_documents=stats.get('max'),
                        indexes=indexes
                    )
                    collections.append(coll_info)
                    
                except Exception as e:
                    self.logger.warning(f"Could not get stats for collection {coll_name}: {e}")
                    # Add collection with minimal info
                    collections.append(CollectionInfo(name=coll_name, database=database_name))
            
            metrics.mark_completed()
            self.performance_metrics.append(metrics)
            
            return sorted(collections, key=lambda x: x.name)
            
        except Exception as e:
            error_msg = f"Failed to get collections for database {database_name}: {e}"
            self.logger.error(error_msg)
            metrics.mark_failed(error_msg)
            self.performance_metrics.append(metrics)
            raise
    
    def execute_query(self, query_info: QueryInfo) -> Tuple[QueryResult, QueryInfo]:
        """
        Execute a MongoDB query and return results with execution details.
        
        Args:
            query_info: Query information and parameters
            
        Returns:
            Tuple of (results, updated_query_info)
        """
        if not self.is_connected():
            raise ConnectionFailure("Not connected to MongoDB")
        
        metrics = PerformanceMetrics(f"query_{query_info.query_type.value}", datetime.now())
        start_time = time.time()
        
        try:
            database = self.current_client[query_info.database]
            collection = database[query_info.collection]
            
            # Execute query based on type
            if query_info.query_type == QueryType.FIND:
                result = self._execute_find_query(collection, query_info)
            elif query_info.query_type == QueryType.COUNT:
                result = self._execute_count_query(collection, query_info)
            elif query_info.query_type == QueryType.DISTINCT:
                result = self._execute_distinct_query(collection, query_info)
            elif query_info.query_type == QueryType.AGGREGATE:
                result = self._execute_aggregate_query(collection, query_info)
            else:
                raise ValueError(f"Unsupported query type: {query_info.query_type}")
            
            # Update query info with results
            execution_time = time.time() - start_time
            query_info.execution_time = execution_time
            query_info.executed_at = datetime.now()
            query_info.result_count = len(result) if isinstance(result, list) else None
            
            # Add to query history
            self.query_history.append(query_info)
            if len(self.query_history) > self.max_history_size:
                self.query_history.pop(0)
            
            metrics.mark_completed()
            self.performance_metrics.append(metrics)
            
            self.logger.info(f"Query executed successfully in {execution_time:.3f}s")
            return result, query_info
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Query execution failed: {e}"
            
            query_info.execution_time = execution_time
            query_info.executed_at = datetime.now()
            query_info.error = error_msg
            
            self.logger.error(error_msg)
            metrics.mark_failed(error_msg)
            self.performance_metrics.append(metrics)
            
            raise
    
    def _execute_find_query(self, collection: Collection, query_info: QueryInfo) -> DocumentList:
        """Execute a find query."""
        cursor = collection.find(
            query_info.query,
            projection=query_info.projection,
            skip=query_info.skip,
            limit=query_info.limit
        )
        
        if query_info.sort:
            cursor = cursor.sort(list(query_info.sort.items()))
        
        documents = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            self._convert_objectids(doc)
        
        return documents
    
    def _execute_count_query(self, collection: Collection, query_info: QueryInfo) -> int:
        """Execute a count query."""
        return collection.count_documents(query_info.query)
    
    def _execute_distinct_query(self, collection: Collection, query_info: QueryInfo) -> List[str]:
        """Execute a distinct query."""
        field = query_info.query.get('field', '_id')
        filter_query = query_info.query.get('filter', {})
        return collection.distinct(field, filter_query)
    
    def _execute_aggregate_query(self, collection: Collection, query_info: QueryInfo) -> DocumentList:
        """Execute an aggregation query."""
        pipeline = query_info.query.get('pipeline', [])
        documents = list(collection.aggregate(pipeline))
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            self._convert_objectids(doc)
        
        return documents
    
    def _convert_objectids(self, obj: Any) -> None:
        """Recursively convert ObjectId instances to strings."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, ObjectId):
                    obj[key] = str(value)
                elif isinstance(value, (dict, list)):
                    self._convert_objectids(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, ObjectId):
                    obj[i] = str(item)
                elif isinstance(item, (dict, list)):
                    self._convert_objectids(item)
    
    def _test_connection(self, client: MongoClient) -> None:
        """Test MongoDB connection with comprehensive checks."""
        # Basic ping
        client.admin.command('ping')
        
        # Test listing databases (requires permissions)
        try:
            client.list_database_names()
        except OperationFailure:
            # User might not have permissions, but connection is still valid
            pass
        
        # Test server info
        try:
            client.server_info()
        except Exception:
            # Server info might not be available, but connection could still work
            pass
    
    def update_document(self, database_name: str, collection_name: str, 
                       document_id: str, updated_document: Dict[str, Any]) -> bool:
        """
        Update a document in the specified collection.
        
        Args:
            database_name: Name of the database
            collection_name: Name of the collection
            document_id: ID of the document to update (ObjectId string)
            updated_document: The complete updated document
            
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ConnectionFailure: If not connected to MongoDB
            OperationFailure: If the update operation fails
            InvalidId: If the document ID is invalid
        """
        if not self.is_connected():
            raise ConnectionFailure("Not connected to MongoDB")
        
        try:
            # Get the collection
            database = self.current_client[database_name]
            collection = database[collection_name]
            
            # Convert string ID to ObjectId if needed
            if isinstance(document_id, str):
                try:
                    object_id = ObjectId(document_id)
                except InvalidId:
                    # If it's not a valid ObjectId, use the string as-is
                    object_id = document_id
            else:
                object_id = document_id
            
            # Remove the _id field from the updated document to avoid conflicts
            update_doc = updated_document.copy()
            if '_id' in update_doc:
                del update_doc['_id']
            
            # Perform the update
            result = collection.replace_one(
                {"_id": object_id},
                update_doc
            )
            
            self.logger.info(f"Document update attempt - Matched: {result.matched_count}, Modified: {result.modified_count}")
            
            return result.matched_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to update document: {str(e)}")
            raise OperationFailure(f"Document update failed: {str(e)}")
    
    def get_connection_status(self) -> ConnectionStatus:
        """Get current connection status."""
        return self.status
    
    def get_query_history(self) -> List[QueryInfo]:
        """Get query execution history."""
        return self.query_history.copy()
    
    def get_performance_metrics(self) -> List[PerformanceMetrics]:
        """Get performance metrics."""
        return self.performance_metrics.copy()
    
    def clear_history(self) -> None:
        """Clear query history and performance metrics."""
        self.query_history.clear()
        self.performance_metrics.clear()
    
    @contextmanager
    def transaction(self, database_name: str):
        """Context manager for MongoDB transactions."""
        if not self.is_connected():
            raise ConnectionFailure("Not connected to MongoDB")
        
        session = self.current_client.start_session()
        try:
            with session.start_transaction():
                yield session
        finally:
            session.end_session()
