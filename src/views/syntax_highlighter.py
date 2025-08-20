"""
Syntax highlighting for JSON and MongoDB queries.

This module provides syntax highlighting for JSON text and MongoDB queries
using PyQt5's QSyntaxHighlighter framework.
"""

import re
from typing import List, Tuple
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for JSON text.
    
    Provides color highlighting for JSON strings, numbers, booleans,
    null values, keys, and structural elements.
    """
    
    def __init__(self, document):
        super().__init__(document)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules for JSON."""
        self.highlighting_rules = []
        
        # JSON Key format (property names)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(34, 139, 34))  # Forest Green
        key_format.setFontWeight(QFont.Bold)
        key_pattern = QRegExp(r'"[^"]*"(?=\s*:)')
        self.highlighting_rules.append((key_pattern, key_format))
        
        # JSON String values
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(139, 69, 19))  # Saddle Brown
        string_pattern = QRegExp(r'"[^"]*"(?!\s*:)')
        self.highlighting_rules.append((string_pattern, string_format))
        
        # JSON Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 0, 255))  # Blue
        number_pattern = QRegExp(r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b')
        self.highlighting_rules.append((number_pattern, number_format))
        
        # JSON Boolean values
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(QColor(255, 20, 147))  # Deep Pink
        boolean_format.setFontWeight(QFont.Bold)
        boolean_pattern = QRegExp(r'\b(true|false)\b')
        self.highlighting_rules.append((boolean_pattern, boolean_format))
        
        # JSON null values
        null_format = QTextCharFormat()
        null_format.setForeground(QColor(128, 128, 128))  # Gray
        null_format.setFontWeight(QFont.Bold)
        null_pattern = QRegExp(r'\bnull\b')
        self.highlighting_rules.append((null_pattern, null_format))
        
        # JSON Structural characters
        structure_format = QTextCharFormat()
        structure_format.setForeground(QColor(128, 0, 128))  # Purple
        structure_format.setFontWeight(QFont.Bold)
        structure_pattern = QRegExp(r'[{}[\]:,]')
        self.highlighting_rules.append((structure_pattern, structure_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to a block of text."""
        # Apply all highlighting rules
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class MongoQueryHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for MongoDB queries.
    
    Extends JSON highlighting with MongoDB-specific operators and functions.
    """
    
    def __init__(self, document):
        super().__init__(document)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules for MongoDB queries."""
        self.highlighting_rules = []
        
        # MongoDB operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(255, 140, 0))  # Dark Orange
        operator_format.setFontWeight(QFont.Bold)
        
        # Query operators
        query_operators = [
            r'\$eq\b', r'\$ne\b', r'\$gt\b', r'\$gte\b', r'\$lt\b', r'\$lte\b',
            r'\$in\b', r'\$nin\b', r'\$exists\b', r'\$type\b', r'\$regex\b',
            r'\$options\b', r'\$where\b', r'\$all\b', r'\$elemMatch\b',
            r'\$size\b', r'\$mod\b'
        ]
        
        # Logical operators
        logical_operators = [
            r'\$and\b', r'\$or\b', r'\$not\b', r'\$nor\b'
        ]
        
        # Update operators
        update_operators = [
            r'\$set\b', r'\$unset\b', r'\$inc\b', r'\$mul\b', r'\$rename\b',
            r'\$setOnInsert\b', r'\$push\b', r'\$pull\b', r'\$addToSet\b',
            r'\$pop\b', r'\$pullAll\b', r'\$each\b', r'\$slice\b', r'\$sort\b',
            r'\$position\b'
        ]
        
        # Aggregation operators
        aggregation_operators = [
            r'\$match\b', r'\$group\b', r'\$sort\b', r'\$limit\b', r'\$skip\b',
            r'\$project\b', r'\$unwind\b', r'\$lookup\b', r'\$addFields\b',
            r'\$replaceRoot\b', r'\$facet\b', r'\$bucket\b', r'\$sample\b',
            r'\$count\b', r'\$sum\b', r'\$avg\b', r'\$min\b', r'\$max\b',
            r'\$first\b', r'\$last\b', r'\$push\b', r'\$addToSet\b'
        ]
        
        # Combine all operators
        all_operators = query_operators + logical_operators + update_operators + aggregation_operators
        
        for op in all_operators:
            pattern = QRegExp(op)
            self.highlighting_rules.append((pattern, operator_format))
        
        # Field names (keys in quotes)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(34, 139, 34))  # Forest Green
        key_format.setFontWeight(QFont.Bold)
        key_pattern = QRegExp(r'"[^"]*"(?=\s*:)')
        self.highlighting_rules.append((key_pattern, key_format))
        
        # String values
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(139, 69, 19))  # Saddle Brown
        string_pattern = QRegExp(r'"[^"]*"(?!\s*:)')
        self.highlighting_rules.append((string_pattern, string_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 0, 255))  # Blue
        number_pattern = QRegExp(r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b')
        self.highlighting_rules.append((number_pattern, number_format))
        
        # Boolean values
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(QColor(255, 20, 147))  # Deep Pink
        boolean_format.setFontWeight(QFont.Bold)
        boolean_pattern = QRegExp(r'\b(true|false)\b')
        self.highlighting_rules.append((boolean_pattern, boolean_format))
        
        # null values
        null_format = QTextCharFormat()
        null_format.setForeground(QColor(128, 128, 128))  # Gray
        null_format.setFontWeight(QFont.Bold)
        null_pattern = QRegExp(r'\bnull\b')
        self.highlighting_rules.append((null_pattern, null_format))
        
        # ObjectId pattern
        objectid_format = QTextCharFormat()
        objectid_format.setForeground(QColor(75, 0, 130))  # Indigo
        objectid_format.setFontWeight(QFont.Bold)
        objectid_pattern = QRegExp(r'ObjectId\("[\da-fA-F]{24}"\)')
        self.highlighting_rules.append((objectid_pattern, objectid_format))
        
        # ISODate pattern
        isodate_format = QTextCharFormat()
        isodate_format.setForeground(QColor(75, 0, 130))  # Indigo
        isodate_pattern = QRegExp(r'ISODate\("[^"]*"\)')
        self.highlighting_rules.append((isodate_pattern, isodate_format))
        
        # Regular expressions
        regex_format = QTextCharFormat()
        regex_format.setForeground(QColor(220, 20, 60))  # Crimson
        regex_format.setFontItalic(True)
        regex_pattern = QRegExp(r'/[^/]*/')
        self.highlighting_rules.append((regex_pattern, regex_format))
        
        # Comments (for documentation purposes)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # Gray
        comment_format.setFontItalic(True)
        comment_pattern = QRegExp(r'//[^\n]*')
        self.highlighting_rules.append((comment_pattern, comment_format))
        
        # Structural characters
        structure_format = QTextCharFormat()
        structure_format.setForeground(QColor(128, 0, 128))  # Purple
        structure_format.setFontWeight(QFont.Bold)
        structure_pattern = QRegExp(r'[{}[\]:,]')
        self.highlighting_rules.append((structure_pattern, structure_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to a block of text."""
        # Apply all highlighting rules
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log files."""
    
    def __init__(self, document):
        super().__init__(document)
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Setup syntax highlighting rules for log files."""
        self.highlighting_rules = []
        
        # Error level
        error_format = QTextCharFormat()
        error_format.setForeground(QColor(255, 0, 0))  # Red
        error_format.setFontWeight(QFont.Bold)
        error_pattern = QRegExp(r'\bERROR\b|\bFATAL\b|\bCRITICAL\b')
        self.highlighting_rules.append((error_pattern, error_format))
        
        # Warning level
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor(255, 165, 0))  # Orange
        warning_format.setFontWeight(QFont.Bold)
        warning_pattern = QRegExp(r'\bWARN\b|\bWARNING\b')
        self.highlighting_rules.append((warning_pattern, warning_format))
        
        # Info level
        info_format = QTextCharFormat()
        info_format.setForeground(QColor(0, 128, 0))  # Green
        info_pattern = QRegExp(r'\bINFO\b')
        self.highlighting_rules.append((info_pattern, info_format))
        
        # Debug level
        debug_format = QTextCharFormat()
        debug_format.setForeground(QColor(128, 128, 128))  # Gray
        debug_pattern = QRegExp(r'\bDEBUG\b')
        self.highlighting_rules.append((debug_pattern, debug_format))
        
        # Timestamps
        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor(0, 0, 255))  # Blue
        timestamp_pattern = QRegExp(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}')
        self.highlighting_rules.append((timestamp_pattern, timestamp_format))
        
        # Class/module names
        module_format = QTextCharFormat()
        module_format.setForeground(QColor(128, 0, 128))  # Purple
        module_pattern = QRegExp(r'[a-zA-Z_][a-zA-Z0-9_.]*\.[a-zA-Z_][a-zA-Z0-9_]*')
        self.highlighting_rules.append((module_pattern, module_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to a block of text."""
        # Apply all highlighting rules
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


def create_highlighter(highlighter_type: str, document):
    """
    Factory function to create syntax highlighters.
    
    Args:
        highlighter_type: Type of highlighter ('json', 'mongo', 'log')
        document: QTextDocument to highlight
        
    Returns:
        QSyntaxHighlighter instance
    """
    if highlighter_type.lower() == 'json':
        return JsonSyntaxHighlighter(document)
    elif highlighter_type.lower() == 'mongo':
        return MongoQueryHighlighter(document)
    elif highlighter_type.lower() == 'log':
        return LogHighlighter(document)
    else:
        raise ValueError(f"Unknown highlighter type: {highlighter_type}")


# Theme configurations for different color schemes
class HighlighterThemes:
    """Color themes for syntax highlighting."""
    
    LIGHT_THEME = {
        'json_key': QColor(34, 139, 34),      # Forest Green
        'json_string': QColor(139, 69, 19),   # Saddle Brown
        'json_number': QColor(0, 0, 255),     # Blue
        'json_boolean': QColor(255, 20, 147), # Deep Pink
        'json_null': QColor(128, 128, 128),   # Gray
        'mongo_operator': QColor(255, 140, 0), # Dark Orange
        'structure': QColor(128, 0, 128),     # Purple
        'comment': QColor(128, 128, 128),     # Gray
    }
    
    DARK_THEME = {
        'json_key': QColor(144, 238, 144),    # Light Green
        'json_string': QColor(255, 218, 185), # Peach Puff
        'json_number': QColor(135, 206, 250), # Light Sky Blue
        'json_boolean': QColor(255, 182, 193), # Light Pink
        'json_null': QColor(192, 192, 192),   # Silver
        'mongo_operator': QColor(255, 215, 0), # Gold
        'structure': QColor(221, 160, 221),   # Plum
        'comment': QColor(169, 169, 169),     # Dark Gray
    }


def apply_theme(highlighter, theme_name: str = 'light'):
    """
    Apply a color theme to a syntax highlighter.
    
    Args:
        highlighter: QSyntaxHighlighter instance
        theme_name: Name of the theme ('light' or 'dark')
    """
    theme = HighlighterThemes.LIGHT_THEME if theme_name == 'light' else HighlighterThemes.DARK_THEME
    
    # This would require modifying the highlighter to accept theme colors
    # Implementation would depend on specific highlighter design
    pass
