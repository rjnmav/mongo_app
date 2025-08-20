# MongoDB Visualizer

A professional desktop application built with PyQt5 for MongoDB database visualization, management, and analysis. Features enterprise-grade architecture with comprehensive logging, configuration management, and modern UI patterns.

![MongoDB Visualizer](https://img.shields.io/badge/MongoDB-Visualizer-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Core Functionality
- **Database Visualization**: Browse databases, collections, and documents with intuitive tree structure
- **Document Viewer**: Multiple view modes (JSON, Table, Tree, Statistics) for comprehensive data analysis
- **Query Interface**: Execute MongoDB queries with syntax highlighting and result visualization
- **Connection Management**: Save and manage multiple database connections with recent history
- **Auto-Connect**: Automatically connects to localhost MongoDB on startup for seamless development
- **Export Capabilities**: Export data in various formats (JSON, CSV, Excel)

### Professional Features
- **MVC Architecture**: Clean separation of concerns with Model-View-Controller pattern
- **Configuration Management**: Centralized settings with environment variable support
- **Comprehensive Logging**: File rotation, console output, and GUI notifications
- **Multi-threading**: Non-blocking database operations with background workers
- **Connection Pooling**: Efficient database connection management
- **Syntax Highlighting**: JSON and MongoDB query syntax highlighting
- **Error Handling**: Robust error handling with user-friendly messages
- **Performance Monitoring**: Built-in performance metrics and optimization

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install
```bash
# Clone the repository
git clone <repository-url>
cd mongo_app

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt pytest pytest-qt black flake8 mypy

# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## Usage

### Basic Usage
```bash
# Start the application
python app.py

# Start with debug logging
python app.py --log-level DEBUG

# Use custom configuration
python app.py --config custom_config.json

# Reset settings to defaults
python app.py --reset-settings
```

### Connecting to MongoDB

#### Auto-Connect (Default)
- **Automatic**: The application automatically connects to `localhost:27017` on startup
- **No Setup Required**: Works immediately if you have MongoDB running locally
- **Configurable**: Can be disabled via File → Auto-Connect to Localhost menu
- **Fallback**: If auto-connect fails, manually connect using the options below

#### Manual Connection
1. Launch the application
2. Click "Connect" or use Ctrl+N
3. Enter your MongoDB connection details:
   - Host and Port
   - Authentication (if required)
   - Database name (optional)
4. Test the connection and save for future use

### Browsing Data
- Use the database tree on the left to navigate
- Double-click collections to view documents
- Use the query interface for custom queries
- Switch between view modes (JSON, Table, Tree, Stats)

### Advanced Features
- **Query Builder**: Construct complex MongoDB queries
- **Export Data**: Export collections or query results
- **Performance Monitoring**: View connection and query statistics
- **Recent Connections**: Quick access to previously used connections

## Architecture

### Directory Structure
```
mongo_app/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── src/                        # Source code package
    ├── config/                 # Configuration management
    │   ├── __init__.py
    │   └── settings.py         # ConfigManager and settings
    ├── models/                 # Data models and database layer
    │   ├── __init__.py
    │   ├── data_models.py      # Data structures and enums
    │   └── mongodb_connection.py # Database connection handling
    ├── controllers/            # Business logic layer
    │   ├── __init__.py
    │   └── database_controller.py # Database operations controller
    ├── views/                  # User interface components
    │   ├── __init__.py
    │   ├── main_window.py      # Main application window
    │   ├── connection_dialog.py # Database connection dialog
    │   ├── document_viewer.py  # Document visualization
    │   └── syntax_highlighter.py # Code syntax highlighting
    └── utils/                  # Utility functions and helpers
        ├── __init__.py
        ├── logging_config.py   # Logging configuration
        └── helpers.py          # Helper functions
```

### MVC Pattern
- **Models**: Data structures, database connections, and business logic
- **Views**: PyQt5 UI components and user interaction handling
- **Controllers**: Coordinate between models and views, handle business logic
3. Click **Test Connection** to verify settings
4. Click **Connect** to establish connection

### Exploring Databases

1. After connecting, the left panel shows all databases
2. Expand a database to see its collections
3. Click on a collection to see basic information
4. Double-click a collection to load its documents

### Viewing Documents

The document viewer provides three views:

#### JSON View
- Pretty-formatted JSON with syntax highlighting
- Shows the raw document structure
- Easy to read and understand document format

#### Table View
- Tabular representation of documents
- Sortable columns
- Good for analyzing structured data
- Handles nested objects by converting them to JSON strings

#### Statistics View
- Field frequency analysis
- Data type distribution
- Sample values for each field
- Useful for understanding collection schema

### Executing Queries

1. Select a collection
2. Enter a MongoDB query in JSON format in the query field
   - Example: `{"status": "active"}`
   - Example: `{"age": {"$gte": 18}}`
3. Click **Execute Query** or press Enter
4. Use **Clear** to reset to show all documents

### Pagination

- **Limit**: Set maximum number of documents to display (1-1000)
- **Skip**: Number of documents to skip (useful for pagination)
- **Refresh**: Reload documents with current settings

## Application Structure

```
mongo_app/
├── main.py                 # Main application entry point
├── mongodb_connector.py    # MongoDB connection and operations
├── connection_dialog.py    # Connection configuration dialog
├── document_viewer.py      # Document visualization widget
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## File Descriptions

### main.py
- Main application window and UI coordination
- Menu bar and status bar management
- Database tree population and interaction handling

### mongodb_connector.py
- MongoDB connection management
- Database and collection operations
- Document querying and retrieval
- Error handling and logging

### connection_dialog.py
- Connection parameter input dialog
- Connection testing functionality
- Input validation and user feedback

### document_viewer.py
- Multi-tab document visualization
- JSON syntax highlighting
- Table view for structured data
- Statistical analysis of collections

## Features in Detail

### Connection Management
- Support for authenticated and non-authenticated connections
- Connection testing before establishing full connection
- Automatic reconnection handling
- Secure password input

### Database Exploration
- Tree view of all databases and collections
- Visual indicators for databases and collections
- Expandable/collapsible tree structure
- Context-aware status updates

### Document Visualization
- Syntax-highlighted JSON view
- Dynamic table generation based on document fields
- Automatic type detection and conversion
- Statistical analysis including:
  - Field frequency across documents
  - Data type distribution
  - Sample values for each field

### Query Capabilities
- Full MongoDB query syntax support
- JSON validation for queries
- Real-time query execution
- Error handling for invalid queries

## System Requirements

- Python 3.7 or higher
- PyQt5 5.15.0 or higher
- pymongo 4.0.0 or higher
- MongoDB server (local or remote)

## Troubleshooting

### Connection Issues
1. Verify MongoDB server is running
2. Check host and port settings
3. Ensure authentication credentials are correct
4. Check firewall settings if connecting to remote server

### Performance Considerations
- Large collections may take time to load
- Use limit parameter to control document count
- Consider using queries to filter large datasets
- Table view may be slower for documents with many fields

### Display Issues
- Ensure PyQt5 is properly installed
- Check display settings if UI appears distorted
- Try different limit values if documents don't display properly

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## Future Enhancements

Potential improvements for future versions:
- Document editing capabilities
- Export functionality (JSON, CSV)
- Advanced query builder
- Index visualization
- Performance monitoring
- Multiple database connections
- Dark theme support
