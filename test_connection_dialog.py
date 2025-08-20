#!/usr/bin/env python3
"""
Test script to show the improved connection dialog.
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

# Add the src directory to the path
sys.path.insert(0, 'src')

from src.views.connection_dialog import ConnectionDialog
from src.controllers.database_controller import DatabaseController


class TestWindow(QMainWindow):
    """Simple test window to show the connection dialog."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection Dialog Test")
        self.setGeometry(100, 100, 300, 200)
        
        # Create controller
        self.controller = DatabaseController()
        
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        
        # Button to show connection dialog
        show_dialog_btn = QPushButton("Show Connection Dialog")
        show_dialog_btn.clicked.connect(self.show_connection_dialog)
        layout.addWidget(show_dialog_btn)
        
        self.setCentralWidget(main_widget)
    
    def show_connection_dialog(self):
        """Show the connection dialog."""
        dialog = ConnectionDialog(self, self.controller)
        result = dialog.exec_()
        
        if result == ConnectionDialog.Accepted:
            print("Connection accepted!")
            connection_info = dialog.get_connection_info()
            print(f"Connection details: {connection_info}")
        else:
            print("Connection cancelled.")


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
