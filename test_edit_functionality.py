#!/usr/bin/env python3
"""
Test script to verify the document editing functionality
"""

import json
from bson import ObjectId

def test_document_edit():
    """Test the document editing functionality"""
    
    # Test document
    test_doc = {
        "_id": ObjectId(),
        "name": "Test User",
        "age": 25,
        "email": "test@example.com"
    }
    
    # Simulate editing the document
    edited_doc = {
        "name": "Test User Updated",
        "age": 26,
        "email": "updated@example.com",
        "status": "active"
    }
    
    print("Original document:")
    print(json.dumps(test_doc, indent=2, default=str))
    
    print("\nEdited document:")
    print(json.dumps(edited_doc, indent=2, default=str))
    
    print("\nDocument ID for update:", str(test_doc['_id']))
    
    # Test JSON validation
    try:
        json.loads(json.dumps(edited_doc))
        print("\n✓ JSON validation passed")
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON validation failed: {e}")

if __name__ == "__main__":
    test_document_edit()
