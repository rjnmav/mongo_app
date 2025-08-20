#!/usr/bin/env python3
"""
Test script to verify button styling issues are fixed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from src.styles.modern_styles import ModernStyles

class ButtonTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Button Style Test')
        self.setGeometry(100, 100, 600, 200)
        
        layout = QVBoxLayout()
        
        # Create test buttons with the problematic object names
        button_layout = QHBoxLayout()
        
        # Execute button test
        execute_btn = QPushButton("Execute Query")
        execute_btn.setObjectName("execute_button")
        button_layout.addWidget(execute_btn)
        
        # Clear button test
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clear_button")
        button_layout.addWidget(clear_btn)
        
        # Other enhanced buttons for comparison
        connect_btn = QPushButton("Connect")
        connect_btn.setObjectName("connect_button")
        button_layout.addWidget(connect_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refresh_button")
        button_layout.addWidget(refresh_btn)
        
        # Regular button without special styling
        regular_btn = QPushButton("Regular Button")
        button_layout.addWidget(regular_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply the enhanced styles
        self.setStyleSheet(ModernStyles.get_complete_stylesheet())

def main():
    app = QApplication(sys.argv)
    
    test_widget = ButtonTestWidget()
    test_widget.show()
    
    print("Test buttons created:")
    print("- Execute Query (purple gradient) - should be visible")
    print("- Clear (gray gradient) - should be visible") 
    print("- Connect (green gradient) - should be visible")
    print("- Refresh (blue gradient) - should be visible")
    print("- Regular Button (default blue) - should be visible")
    print("\nIf Execute and Clear buttons are invisible, the issue persists.")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
