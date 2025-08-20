#!/usr/bin/env python3
"""
MongoDB Visualizer - Professional Desktop Application

A comprehensive PyQt5-based desktop application for MongoDB database
visualization, management, and analysis with enterprise-grade features.

Usage:
    python app.py [--config CONFIG_FILE] [--log-level LEVEL]

Author: MongoDB Visualizer Team
Version: 1.0.0
License: MIT
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

from src.config.settings import get_config
from src.utils.logging_config import initialize_logging, get_logger
from src.views.main_window import MainWindow
from src.utils.helpers import show_error_message


class MongoDBVisualizerApp(QApplication):
    """
    Main application class for MongoDB Visualizer.
    
    Handles application lifecycle, error handling, and global settings.
    """
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Application metadata
        self.setApplicationName("MongoDB Visualizer")
        self.setApplicationVersion("1.0.0")
        self.setApplicationDisplayName("MongoDB Visualizer")
        self.setOrganizationName("MongoDB Visualizer Team")
        self.setOrganizationDomain("mongodbvisualizer.com")
        
        # Set application style
        self.setStyle('Fusion')
        
        # Initialize configuration and logging
        self.config = get_config()
        self.log_manager = initialize_logging(self.config)
        self.logger = get_logger(__name__)
        
        # Main window
        self.main_window = None
        
        # Setup global exception handling
        sys.excepthook = self.handle_exception
        
        self.logger.info("MongoDB Visualizer application initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the application.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Show splash screen
            splash = self.create_splash_screen()
            splash.show()
            self.processEvents()
            
            # Initialize main window
            splash.showMessage("Loading main window...", Qt.AlignBottom | Qt.AlignCenter)
            self.processEvents()
            
            self.main_window = MainWindow()
            
            splash.showMessage("Finalizing setup...", Qt.AlignBottom | Qt.AlignCenter)
            self.processEvents()
            
            # Close splash screen and show main window
            splash.finish(self.main_window)
            self.main_window.show()
            
            self.logger.info("Application initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            self.show_critical_error("Initialization Error", 
                                   f"Failed to initialize the application: {str(e)}")
            return False
    
    def create_splash_screen(self) -> QSplashScreen:
        """Create and configure the splash screen."""
        # Create a simple splash screen with text
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        
        # Add text to splash screen
        splash.showMessage("MongoDB Visualizer v1.0.0\nLoading...", 
                          Qt.AlignCenter | Qt.AlignBottom, Qt.black)
        
        return splash
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            self.quit()
            return
        
        # Log the exception
        import traceback
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.critical(f"Uncaught exception: {exc_value}\n{tb_str}")
        
        # Show error dialog
        self.show_critical_error("Unexpected Error", 
                               f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
                               f"The application may become unstable. Please restart.")
    
    def show_critical_error(self, title: str, message: str):
        """Show a critical error dialog."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def cleanup(self):
        """Cleanup application resources."""
        try:
            if self.main_window:
                # Save settings before closing
                self.main_window.save_settings()
                
            # Save configuration
            self.config.save_config()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="MongoDB Visualizer - Database visualization and management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                          # Start with default settings
  python app.py --log-level DEBUG        # Enable debug logging
  python app.py --config custom.json     # Use custom configuration file
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='MongoDB Visualizer 1.0.0'
    )
    
    parser.add_argument(
        '--reset-settings',
        action='store_true',
        help='Reset all application settings to defaults'
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        ('PyQt5', 'PyQt5'),
        ('pymongo', 'pymongo'),
        ('psutil', 'psutil')
    ]
    
    missing_modules = []
    
    for module_name, import_name in required_modules:
        try:
            __import__(import_name)
        except ImportError:
            missing_modules.append(module_name)
    
    if missing_modules:
        print(f"Error: Missing required dependencies: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def setup_environment():
    """Setup application environment and paths."""
    # Create application data directory
    app_data_dir = Path.home() / ".mongodb_visualizer"
    app_data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (app_data_dir / "logs").mkdir(exist_ok=True)
    (app_data_dir / "exports").mkdir(exist_ok=True)
    (app_data_dir / "backups").mkdir(exist_ok=True)
    
    return True


def main():
    """Main application entry point."""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("Error: Failed to setup application environment")
        sys.exit(1)
    
    # Handle reset settings
    if args.reset_settings:
        try:
            from PyQt5.QtCore import QSettings
            settings = QSettings("MongoDBVisualizer", "Settings")
            settings.clear()
            settings.sync()
            print("Application settings have been reset to defaults.")
            return 0
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return 1
    
    # Create application
    # Enable high DPI support before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = MongoDBVisualizerApp(sys.argv)
    
    # Apply command-line options
    if args.log_level:
        log_manager = app.log_manager
        if log_manager:
            log_manager.set_level(args.log_level)
    
    # Initialize application
    if not app.initialize():
        return 1
    
    # Setup signal handlers for graceful shutdown
    import signal
    def signal_handler(signum, frame):
        app.logger.info(f"Received signal {signum}, shutting down gracefully...")
        app.cleanup()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run application
    try:
        exit_code = app.exec_()
        app.cleanup()
        return exit_code
        
    except Exception as e:
        app.logger.critical(f"Fatal error in main loop: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
