# Auto-Connect to Localhost Feature

## Overview
The MongoDB Visualizer now automatically connects to a local MongoDB instance on startup, providing a seamless development experience.

## Features

### Automatic Connection
- **Default Behavior**: Automatically connects to `localhost:27017` on application startup
- **Delay**: Connection attempt is delayed by 500ms to ensure UI is fully loaded
- **Silent Failure**: If connection fails, the application continues normally without error dialogs
- **Configuration-Driven**: Uses the default host and port from application configuration

### Configuration Control
- **Settings Location**: Auto-connect behavior is controlled via `src/config/settings.py`
- **DatabaseConfig Property**: `auto_connect_localhost: bool = True`
- **Configurable Host/Port**: Uses `default_host` and `default_port` from DatabaseConfig

### User Interface Control
- **Menu Toggle**: File → Auto-Connect to Localhost (checkable menu item)
- **Persistent Setting**: Toggle state is saved to configuration file
- **Real-time Control**: Can be enabled/disabled without restarting the application

## Usage

### Enable/Disable Auto-Connect
1. Open the application
2. Go to **File** menu
3. Toggle **Auto-Connect to Localhost** checkbox
4. Setting is automatically saved and will persist for future sessions

### Manual Connection Override
- If auto-connect is disabled or fails, users can still connect manually via:
  - File → Connect to Database...
  - Toolbar Connect button
  - Recent Connections menu

### Configuration via File
Edit `src/config/settings.py` and modify the `DatabaseConfig` class:

```python
@dataclass
class DatabaseConfig:
    default_host: str = "localhost"        # Change host
    default_port: int = 27017             # Change port
    auto_connect_localhost: bool = True   # Enable/disable auto-connect
```

## Implementation Details

### Code Changes
1. **DatabaseConfig**: Added `auto_connect_localhost` property
2. **MainWindow**: Added `auto_connect_localhost()` method
3. **MainWindow**: Added delayed auto-connection on startup
4. **UI Menu**: Added toggle option in File menu
5. **Settings Persistence**: Auto-saves configuration changes

### Connection Process
1. Application starts and initializes UI
2. After 500ms delay, `auto_connect_localhost()` is called
3. Method checks if auto-connect is enabled in configuration
4. Creates ConnectionInfo with default host/port settings
5. Attempts connection via DatabaseController
6. On success: displays databases and collections
7. On failure: logs warning and continues normally

### Error Handling
- Connection failures are logged as warnings, not errors
- No user-facing error dialogs for auto-connect failures
- Users can always connect manually if auto-connect fails
- Graceful degradation when MongoDB is not available

## Benefits

### Developer Experience
- **Zero Configuration**: Works out-of-the-box for local development
- **Fast Startup**: Immediate access to local MongoDB data
- **Non-Intrusive**: Doesn't interfere if MongoDB isn't running

### Production Use
- **Configurable**: Can be disabled for production deployments
- **Flexible**: Supports custom host/port configurations
- **Safe**: No security implications since it only attempts localhost connections

## Log Messages

When auto-connect is working:
```
INFO - Attempting auto-connection to localhost:27017...
INFO - Successfully connected to MongoDB
INFO - Connected to database successfully
INFO - Loaded X databases
```

When auto-connect is disabled:
```
INFO - Auto-connection to localhost is disabled in configuration
```

When auto-connect fails:
```
WARNING - Auto-connection to localhost failed: [error details]
```

## Future Enhancements

Potential improvements:
- Support for multiple auto-connect targets
- Retry logic with exponential backoff
- Auto-connect to recently used connections
- Connection validation before UI display
- Auto-discovery of local MongoDB instances
